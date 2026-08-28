#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include "ae_transformation.h"

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: exact pairs.tsv\n";
        return 2;
    }
    std::ifstream in(argv[1]);
    if (!in) return 3;
    std::string line;
    std::vector<int> solved_sources;
    int attempts = 0;
    int positives = 0;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string gs, ts, src, tgt;
        if (!std::getline(ss, gs, '\t') || !std::getline(ss, ts, '\t') ||
            !std::getline(ss, src, '\t') || !std::getline(ss, tgt, '\t')) return 4;
        int g = std::stoi(gs), t = std::stoi(ts);
        bfl::bf_tt<8> f, h;
        f.assign(src);
        h.assign(tgt);
        ae::affine_mapping<8> am(ae::affine_mapping<8>::init::zero);
        ++attempts;
        bool eq = ae::is_affine_equivalent<8>(f, h, am);
        if (eq) {
            ++positives;
            solved_sources.push_back(g);
            std::cout << "NIST_AE_VERIFIED " << g << " -> " << t << "\n";
        } else {
            std::cout << "NIST_AE_NO " << g << " -> " << t << "\n";
        }
    }
    std::sort(solved_sources.begin(), solved_sources.end());
    solved_sources.erase(std::unique(solved_sources.begin(), solved_sources.end()), solved_sources.end());
    std::cout << "NIST_AE_SUMMARY attempts=" << attempts
              << " positives=" << positives
              << " solved_sources=" << solved_sources.size() << "\n";
    if (solved_sources.size() != 21) {
        std::cerr << "UNSOLVED_SOURCE_COUNT " << (21 - solved_sources.size()) << "\n";
        return 5;
    }
    std::cout << "LEVEL5_DIM8_ANTIPERIOD_RESIDUAL_CLOSED\n";
    return 0;
}
