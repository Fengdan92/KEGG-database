#include <fstream>
#include <string>
#include <cstdlib>
#include <mpi.h>

int main(int argc, char *argv[])
{
	MPI_Init(NULL, NULL);
	int world_size;
	MPI_Comm_size(MPI_COMM_WORLD, &world_size);
	int world_rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);

	int M = std::stoi(argv[1]);
	//int job_id = M*world_size + world_rank;

	std::ifstream input_list;
	input_list.open("list");

	int file_index = 0;
	std::string line;
	char line2[1024];
	char job_name[50];
	while(std::getline(input_list, line))
	{
		if(file_index == M)
		{
			//std::cout << line << '\n';
			std:strncpy(line2, line.c_str(), sizeof(line2));
			line2[sizeof(line2) - 1] = 0;
			std::sprintf(job_name, "python %s %d", line2, world_rank);
			//std::sprintf(job_name, "python test.py");
			std::system(job_name);
			break;
		}
		file_index += 1;
	}

	MPI_Finalize();

	return(0);
}
