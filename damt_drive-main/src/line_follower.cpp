
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "emaros_floor_sensors/msg/colors.hpp"
#include "tf2_msgs/msg/tf_message.hpp"
#include <fstream>
#include <iostream>
#include <cmath>
#include <algorithm>

class LineFollower : public rclcpp::Node
{
public:
    LineFollower() : Node("line_follower")
    {
        //publisht Anpssung der Fahrrichtung
        //msg.angular.z positiv = nach links drehen, negativ = nach rechts drehen;
        //motor_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("line_follower", 10); ----------- überflüssig ----------
        motor_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

        //abboniert bodensensordaten
        sensor_sub_ = this->create_subscription<emaros_floor_sensors::msg::Colors>(
            "/floor_sensors", 10,
            [this](const emaros_floor_sensors::msg::Colors::SharedPtr msg) {
                // Sensoren: 0 = rechts außen, 1 = links außen, 2 = rechts innen, 3 = links innen
                sensors_[0] = (msg->r_0 + msg->g_0 + msg->b_0); //rechts außen
                sensors_[1] = (msg->r_3 + msg->g_3 + msg->b_3); //links außen
                sensors_[2] = (msg->r_1 + msg->g_1 + msg->b_1); //rechts innen
                sensors_[3] = (msg->r_2 + msg->g_2 + msg->b_2); //links innen

                // Bodenmessung
                // std::ofstream file;
                // file.open("sensormessug_.txt", std::ios::app);
                // if (file.is_open()) {
                //     file << sensors_[0] << " " << sensors_[2] << " " << sensors_[3] << " " << sensors_[1] << std::endl;
                //     file.close();
                // }
            });
            
        // ----------- veraltet --------------
        //abboniert Fahrdaten der tf || aufgrund von Ungenauigkeit eingestellt
        // tf_sub_ = this->create_subscription<tf2_msgs::msg::TFMessage>(
        // "/tf", 10,
        // [this](const tf2_msgs::msg::TFMessage::SharedPtr msg) {
        //     for (const auto &transform : msg->transforms) {
        //         if (transform.child_frame_id == "emaros_base_link") {
        //             double trans_x = transform.transform.translation.x;
        //             double trans_y = transform.transform.translation.y;
        //             yaw_deg = (2.0 * std::atan2(transform.transform.rotation.z, transform.transform.rotation.w)) * (180.0 / M_PI);
        //             if (yaw_deg < 0.0){
        //                 yaw_deg += 360.0;
        //             }
        //             std::ofstream file;
        //             file.open("tf_v.txt", std::ios::app);
        //             if (file.is_open()) {
        //                 file << "trans_x: " << trans_x << ", trans_y: " << trans_y << ", yaw_deg: " << yaw_deg << std::endl;
        //                 file.close();
        //             }
        //         }
        //     }
        // });
        // Trennung für asyncrone Verarbeitung
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20),
            std::bind(&LineFollower::control_loop, this));
        timer2_ = this->create_wall_timer(
            std::chrono::milliseconds(20),
            std::bind(&LineFollower::robot_states, this));
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr motor_pub_;
    rclcpp::Subscription<emaros_floor_sensors::msg::Colors>::SharedPtr sensor_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::TimerBase::SharedPtr timer2_;

    //rclcpp::Subscription<tf2_msgs::msg::TFMessage>::SharedPtr tf_sub_;
    int sensors_[4] = {0, 0, 0, 0};
    // true = Schwarze Linie || false = keine schwarze Linie
    bool sensor_states[4] = {true, true, false , false};
    enum RobotStates{
        defaultState = 0,
        errorState = -1,
        rechtsabbiegen = 1,
        linksabbiegen = 2,
    };
    enum SensorPosition {
        RECHTS_AUSSEN = 0,
        LINKS_AUSSEN  = 1,
        RECHTS_INNEN  = 2,
        LINKS_INNEN   = 3
    };
    //Schwellenwert, zum erkennen von Linien
    const int threshold_innen = 13000;
    const int threshold_außen = 8000;
    const double drivespeed = 0.1;
    const int min_diff = 8000;
    const int max_diff = 25000;
    int diff;
    int error_index = 0;
    double error;
    double last_error;
    double kp = 0.1;
    double ki = 0.0;
    double kd = 1.0;
    double ks = 0.1;
    double integral;
    double error_history[50] = {0};
    double sum = 0;
    //rechts innen: 14082, links innen: 12098 ---> zu weit rechts, leicht nach links lenken ----> 
    std::ofstream file;

    void control_loop(){
        // Schleife zum checken der Linien        
        for (int i = 0; i < 2; ++i) {
            // Wenn Helligkeit eines Sensors unter 16000 fällt dann liegt er über einer schwarzen Linie
            sensor_states[i] = (sensors_[i] <= threshold_außen);
        }
        if (sensors_[2] < threshold_innen || sensors_[3] < threshold_innen) {
            // diff negativ -> es wird nach rechts gesteuert | rechts < links -> Roboter ist zu weit links
            // diff positiv -> es wird nach links gesteuert | rechts > links -> Roboter ist zu weit rechts
            diff = sensors_[2] - sensors_[3];
            if (diff < -500) {
                sensor_states[2] = true;
            } else if (diff > 500) {
                sensor_states[3] = true;
            } else{
                sensor_states[2] = false;
                sensor_states[3] = false;
                error = -(last_error/2); // Invertieren und auspendeln, wenn die linie erreicht
                return;
            }
            error = ((double)diff / max_diff) + sensor_states[0] * -0.2 + sensor_states[1] * 0.2;
            error_history[error_index] = error;
            error_index = (error_index + 1) % 50;

            for (int i = 0; i < 50; ++i) {
                sum += error_history[i];
                // sum entweder in error einrechnen oder als separate Variable verwenden
            }
            sum = sum/50;
            error = ((double)diff / max_diff) + sensor_states[0] * -0.2 + sensor_states[1] * 0.2;
        }else {
            sensor_states[2] = true;
            sensor_states[3] = true;
        }
    }

    void robot_states(){
        //file.open("PID_kalibrierung_.txt", std::ios::app); //DEBUG zum Messen der Fahrdaten
        auto msg = geometry_msgs::msg::Twist();
        auto now = this->get_clock()->now();

        switch (checkSensorStates()){
             // Sensoren: 0 = rechts außen || 1 = links außen || 2 = rechts innen || 3 = links innen
            case rechtsabbiegen:  //////////     L-Kreuzung-rechts    ////////////
                // file << "rechts abbiegen bei: "<< "links außen: " << sensors_[1] << " links innen: " << sensors_[3] << " rechts innen: " << sensors_[2] << " rechts außen: " << sensors_[0] << std::endl
                ausrichten(-0.1, -1.0, 0.75);
                break;
            case linksabbiegen:  //////////     L-Kreuzung-links    ///////////
                // file << "links abbiegen bei: "<< "links außen: " << sensors_[1] << " links innen: " << sensors_[3] << " rechts innen: " << sensors_[2] << " rechts außen: " << sensors_[0] << std::endl;
                ausrichten(-0.1, 1.0, 0.75);
                break;
            case errorState:  //////////     to do    ///////////
                // file << "Linie verlassen bei: "<< "links außen: " << sensors_[1] << " links innen: " << sensors_[3] << " rechts innen: " << sensors_[2] << " rechts außen: " << sensors_[0] << std::endl;
                ausrichten(-drivespeed, -(2 * last_error), 0.75);
                break;
            case defaultState:  //////////     Normale Fahrt    ///////////
                msg.linear.x = drivespeed;
                //gegenlenken abhängig zum Fehler

                double derivative = error - last_error;
                integral += error;
                integral = std::clamp(integral, -10.0, 10.0);

                msg.angular.z =  kp * error + ki * integral + kd * derivative + ks * sum; // PID regler + Gegengewicht bei zu starkem Lenken --> funktioniert nicht gut, vermutlich zu viele Regler. Neuer Ansatz wäre erforderlich
                msg.angular.z = std::clamp(msg.angular.z, -0.15, 0.15); // begrenzung der Lenkbewegung
                last_error = error; 
                // file << "error: " << error << " | interal: " << integral  << " | derivative: " << derivative  <<" | sum: " << sum << " | msg.angular.z: " << msg.angular.z <<  std::endl;
                break;
        }
        // file.close();
        motor_pub_->publish(msg);
        }
    // nicht asynchrones Abbiergen, blockiert robot_states --> bessere Lösung in damt_vision mit state machine
    void ausrichten(double linear_x, double angular_z, double dauer_in_sekunden) {
        auto start = this->get_clock()->now();
        auto twist = geometry_msgs::msg::Twist();
        twist.linear.x = linear_x;
        twist.angular.z = angular_z;

        rclcpp::Rate rate(20);
        while ((this->get_clock()->now() - start).seconds() < dauer_in_sekunden && rclcpp::ok()) {
            motor_pub_->publish(twist);
            rate.sleep();
        }
    }

    int checkSensorStates(){
        // true = schwarze Linie erkannt, false = keine schwarze Linie erkannt
        if(sensor_states[LINKS_AUSSEN] == false && sensor_states[LINKS_INNEN] == true && sensor_states[RECHTS_INNEN] == false && sensor_states[RECHTS_AUSSEN] == false){
            return linksabbiegen;
        }else if(sensor_states[LINKS_AUSSEN] == false && sensor_states[LINKS_INNEN] == true && sensor_states[RECHTS_INNEN] == false && sensor_states[RECHTS_AUSSEN] == false){
            return rechtsabbiegen;
        }else if(sensor_states[LINKS_AUSSEN] == false && sensor_states[LINKS_INNEN] == true && sensor_states[RECHTS_INNEN] == false && sensor_states[RECHTS_AUSSEN] == false){
            return errorState;
        }else{
            return defaultState;
        }
    }

};

int main(int argc, char * argv[]){
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<LineFollower>());
    rclcpp::shutdown();
    return 0;
}
