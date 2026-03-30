#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <sstream>

using namespace std;

class SensorAnalyzer {
public:
    void processFile(const string& inputFile, const string& outputFile) {
        ifstream infile(inputFile);
        ofstream outfile(outputFile, ios::app);

        if (!infile.is_open() || !outfile.is_open()) {
            cerr << "Fehler beim Öffnen der Datei!" << endl;
            return;
        }

        vector<float> values;
        float val;

        // Alle Zahlen aus der Datei einlesen
        while (infile >> val) {
            values.push_back(val);
        }

        // Mittelwert berechnen
        float mean = accumulate(values.begin(), values.end(), 0.0) / values.size();

        // Median berechnen
        sort(values.begin(), values.end());
        float median;
        size_t n = values.size();
        if (n % 2 == 0) {
            median = (values[n/2 - 1] + values[n/2]) / 2.0;
        } else {
            median = values[n/2];
        }

        // Spannweite berechnen (max - min)
        int range = values.back() - values.front();

        // Ergebnisse in die Ausgabedatei schreiben
        outfile << "Mittelwert: " << mean << "  |  ";
        outfile << "Median: " << median << "  |  ";
        outfile << "Spannweite: " << range << "\n";
    }

    void processColumns2and3(const string& inputFile, const string& outputFile) {
        ifstream infile(inputFile);
        ofstream outfile(outputFile, ios::app);

        if (!infile.is_open() || !outfile.is_open()) {
            cerr << "Fehler beim Öffnen der Datei!" << endl;
            return;
        }
        vector<int> values;
        string line;

        while (getline(infile, line)) {
            istringstream iss(line);
            int val1, val2, val3, val4;
            if (iss >> val1 >> val2 >> val3 >> val4) {
                values.push_back(val2); // Wert 2 (Index 1)
                values.push_back(val3); // Wert 3 (Index 2)
            }
        }

        // Mittelwert
        float mean = accumulate(values.begin(), values.end(), 0.0) / values.size();

        // Median
        sort(values.begin(), values.end());
        double median;
        size_t n = values.size();
        if (n % 2 == 0)
            median = (values[n/2 - 1] + values[n/2]) / 2.0;
        else
            median = values[n/2];

        // Spannweite
        int range = values.back() - values.front();

        // Ausgabe
        outfile << "[Wert 2 & 3] Mittelwert: " << mean
                << ", Median: " << median
                << ", Spannweite: " << range << "\n";
    }
};

int main() {
    SensorAnalyzer analyzer;
    analyzer.processFile("sensormessug_.txt", "messergebnisse.txt");
    return 0;
}
