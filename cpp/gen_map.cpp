#include <iostream>

#include "simplex.h"
#include "stdlib.h"

#include <trng/uniform_int_dist.hpp>
#include <trng/mt19937.hpp>

constexpr int OCTAVES = 8;
constexpr int PERSISTENCE = 0.5f;
constexpr int LUNCARITY = 2.0f;
const float scaling_factor=0.0078125;

int* gen_map(float seed, int idx, int idy, int map_size=96) {
    // Negative seeds wrap-around
    const int array_size = map_size*map_size;
    trng::mt19937 mt((unsigned long)seed);
    static trng::uniform_int_dist U(0,3);
    int idx_abs_base = idx * map_size;
    int idy_abs_base = idy * map_size;
    int *map = new int[array_size];
    float val;
    for(int i = 0; i < array_size; i++) {
        val = fbm_noise3((idx_abs_base+(i%map_size)) * scaling_factor,
                (idy_abs_base+(i/map_size)) * scaling_factor,
                seed, OCTAVES, PERSISTENCE, LUNCARITY);
        if(-.2 < val && val < 0) {
            map[i] = U(mt);
        } else {
            map[i] = 255;
        }

    }
    return map;
}
int* gen_map2(float seed, int idx, int idy, int map_size=96) {
    // Negative seeds wrap-around
    const int array_size = map_size*map_size;
    trng::mt19937 mt((unsigned long)seed);
    static trng::uniform_int_dist U(0,3);
    int idx_abs_base = idx * map_size;
    int idy_abs_base = idy * map_size;
    int *map = new int[array_size];
    float val;
    int y_coord;
    int x_coord;
    for(int i = 0; i < array_size; i++) {
        y_coord = i/map_size;
        x_coord = i-(y_coord*map_size);
        //std::cout << "x_coord: " << x_coord << std::endl;
        val = fbm_noise3((idx_abs_base+(x_coord)) * scaling_factor,
                (idy_abs_base+(y_coord)) * scaling_factor,
                seed, OCTAVES, PERSISTENCE, LUNCARITY);
        if(-.2 < val && val < 0) {
            map[i] = U(mt);
        } else {
            map[i] = 255;
        }

    }
    return map;
}
int** gen_map3(float seed, int idx, int idy, int map_size=96) {
    // Negative seeds wrap-around
    trng::mt19937 mt((unsigned long)seed);
    static trng::uniform_int_dist U(0,3);
    int idx_abs_base = idx * map_size;
    int idy_abs_base = idy * map_size;
    int **map = new int*[map_size];
    float val;
    for(int row = 0; row < map_size; row++) {
        map[row] = new int[map_size];
        for(int col = 0; col < map_size; col++) {
            val = fbm_noise3((idx_abs_base+(col)) * scaling_factor,
                    (idy_abs_base+(row)) * scaling_factor,
                    seed, OCTAVES, PERSISTENCE, LUNCARITY);
            if(-.2 < val && val < 0) {
                map[row][col] = U(mt);
            } else {
                map[row][col] = 255;
            }
        }
    }

    return map;
}
void print_map(int *map, int map_size) {
    const int array_size = map_size*map_size;
    for(int i =0; i < array_size; i++) {
        std::cout << map[i] << ",";
    }
    std::cout << std::endl;
}

bool compare_map(int* map1, int* map2, int map_size) {
    const int array_size = map_size*map_size;
    for(int i =0; i < array_size; i++) {
        if(map1[i] != map2[i]){
            std::cout << i;
            return false;
        }
    }
    return true;
}

bool comp_2d(int* map1, int** map_2d, int map_size) {
    const int array_size = map_size*map_size;
    for(int i =0; i < array_size; i++) {
        if(map1[i] != map_2d[i/map_size][i%map_size]){
            std::cout << i;
            return false;
        }
    }
    return true;
}

