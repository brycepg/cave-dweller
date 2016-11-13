#include <iostream>
#include <ios>
#include <chrono>

#include "gen_map.h"

typedef std::chrono::high_resolution_clock Clock;

int main(int argc, char* argv[]) {
    std::cout << std::boolalpha;
    std::ios_base::sync_with_stdio(false);
    int map_size = 96;
    auto t1 = Clock::now();
    int* map = gen_map(0, 0, 0, map_size);
    auto t2 = Clock::now();
    std::cout << "m1: Duration: " << std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count()/(1000.0*1000) << " m" << std::endl;
    t1 = Clock::now();
    int *map2 = gen_map2(0,0,0,map_size);
    t2 = Clock::now();
    std::cout << "m2: Duration: " << std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count()/(1000.0*1000) << " m" << std::endl;
    bool same = compare_map(map, map2, map_size);
    std::cout << "Same: " << same << std::endl;

    t1 = Clock::now();
    int **map3 = gen_map3(0,0,0,map_size);
    t2 = Clock::now();
    std::cout << "m2: Duration: " << std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count()/(1000.0*1000) << " m" << std::endl;
    bool same3 = comp_2d(map, map3, map_size);
    std::cout << "Same: " << same3 << std::endl;
    //print_map(map, map_size);
    return 0;
}
