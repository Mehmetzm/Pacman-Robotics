#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "emaros_i2c_lib/floor_leds.hpp"

class MotorDriver : public rclcpp::Node
{
public:
    MotorDriver() : Node("damt_driver"){
        //publisht die Fahrrichtung
        twist_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);

        //abboniert die Fahrdaten der bodensensorbasierten Steuerung
        line_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "line_follower", 5,
            [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
                this->handle_input_msg(msg, "line_follower");
                //twist_pub_->publish(*msg);
        });
        //abboniert die Fahrdaten der kamerabasierten Steuerung
        camera_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "camera_follower", 5,
            [this](const geometry_msgs::msg::Twist::SharedPtr msg) {
                this->handle_input_msg(msg, "camera_follower");
                //twist_pub_->publish(*msg);
        });
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20),
            std::bind(&MotorDriver::control_loop, this));
    };

private:
    std::vector<geometry_msgs::msg::Twist::SharedPtr> line_buffer;
    std::vector<geometry_msgs::msg::Twist::SharedPtr> camera_buffer;
    geometry_msgs::msg::Twist line;
    geometry_msgs::msg::Twist camera;

    void handle_input_msg(const geometry_msgs::msg::Twist::SharedPtr msg, const std::string& source) {
        if (source == "line_follower"){
            line_buffer.push_back(msg);
            if (line_buffer.size() > 5) {
                line_buffer.erase(line_buffer.begin());
            }
        }else if (source == "camera_follower") {
            camera_buffer.push_back(msg);
            if (camera_buffer.size() > 5) {
                camera_buffer.erase(camera_buffer.begin());
            }
        }
        return;
    }
    void control_loop(){
        auto output = geometry_msgs::msg::Twist();
        bool has_line = !line_buffer.empty();
        bool has_camera = !camera_buffer.empty();
        int anzahl = 0;

        if (!has_line && !has_camera) {
            return;
        }

        geometry_msgs::msg::Twist::SharedPtr line_msg;
        geometry_msgs::msg::Twist::SharedPtr camera_msg;

        if (has_line) {
            anzahl++;
            line_msg = line_buffer.front();
            line_buffer.erase(line_buffer.begin());
        } else {
            line_msg = std::make_shared<geometry_msgs::msg::Twist>();
        }

        if (has_camera) {
            anzahl++;
            camera_msg = camera_buffer.front();
            camera_buffer.erase(camera_buffer.begin());
        } else {
            camera_msg = std::make_shared<geometry_msgs::msg::Twist>();
        }

        // Komponentenweise Addition
        output.linear.x  = std::max(line_msg->linear.x, camera_msg->linear.x);
        output.linear.y  = std::max(line_msg->linear.y, camera_msg->linear.y);
        output.linear.z  = std::max(line_msg->linear.z, camera_msg->linear.z);

        output.angular.x = (line_msg->angular.x + camera_msg->angular.x) / std::max(anzahl, 1);
        output.angular.y = (line_msg->angular.y + camera_msg->angular.y) / std::max(anzahl, 1);
        output.angular.z = (line_msg->angular.z + camera_msg->angular.z) / std::max(anzahl, 1);

        // Publizieren
        twist_pub_->publish(output);
        return;
    }
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr twist_pub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr line_sub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr camera_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char **argv){
    EMAROs::Base::FloorLeds floor_leds;
    for (int i=0; i<4 ;i++){
        floor_leds.setLed(i, 250.0 / 255.0);
    }
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MotorDriver>());
    rclcpp::shutdown();
    return 0;
}