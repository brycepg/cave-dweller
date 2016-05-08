int* gen_map(float seed, int idx, int idy, int map_size=96);
int* gen_map2(float seed, int idx, int idy, int map_size=96);
int** gen_map3(float seed, int idx, int idy, int map_size=96);
void print_map(int *map, int map_size);
bool compare_map(int* map1, int* map2, int map_size);
bool comp_2d(int* map1, int** map_2d, int map_size);
