#include <algorithm>
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
    int attempts=0, positives=0, negatives=0, mc3=0, mc4=0;
    while (std::getline(in,line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string is,mcs,lns,src,tgt,bits;
        if (!std::getline(ss,is,'\t') || !std::getline(ss,mcs,'\t') ||
            !std::getline(ss,lns,'\t') || !std::getline(ss,src,'\t') ||
            !std::getline(ss,tgt,'\t') || !std::getline(ss,bits,'\t')) return 4;
        int idx=std::stoi(is), mc=std::stoi(mcs), ln=std::stoi(lns);
        bfl::bf_tt<6> f,h;
        f.assign(src);
        h.assign(tgt);
        ae::affine_mapping<6> am(ae::affine_mapping<6>::init::zero);
        ++attempts;
        bool eq=ae::is_affine_equivalent<6>(f,h,am);
        if (eq) {
            ++positives;
            if (mc==3) ++mc3; else if (mc==4) ++mc4; else return 6;
            std::cout << "RESIDUAL_AE_VERIFIED candidate=" << idx
                      << " target=MC" << mc << ":" << ln
                      << " bits=" << bits << "\n";
        } else {
            ++negatives;
            std::cout << "RESIDUAL_AE_NO candidate=" << idx
                      << " target=MC" << mc << ":" << ln
                      << " bits=" << bits << "\n";
        }
    }
    std::cout << "RESIDUAL_AE_SUMMARY attempts=" << attempts
              << " positives=" << positives
              << " negatives=" << negatives
              << " mc3=" << mc3 << " mc4=" << mc4 << "\n";
    if (attempts != 512 || positives != 512 || negatives != 0) return 5;
    std::cout << "LEVEL5_FIRST_NONABSORPTION_RESIDUAL_CLOSED\n";
    return 0;
}
