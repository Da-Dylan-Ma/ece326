#include <cstdio>
#include <cstring>
#include <iostream>
using std::cout;
using std::cerr;
using std::endl;

int TERMINATE = -1;

static int usage(const char * prog) {
	fprintf(stderr, "usage: %s [-h] [-f FILE|-i SEED [-r FILE]] [[-s] -a FILE NUM]\n", prog);
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -h:\tDisplay this message\n");
	fprintf(stderr, " -f:\tUse file-based shoe\n");
	fprintf(stderr, " -i:\tUse random-based shoe (default)\n");
	fprintf(stderr, " -r:\tRecord random-based shoe to file\n");
	fprintf(stderr, " -a:\tPlay automatically using strategy chart\n");
	fprintf(stderr, " -s:\tSilent mode\n");
	fprintf(stderr, " FILE:\tFile name for associated option\n");
	fprintf(stderr, " SEED:\trandom seed\n");
	fprintf(stderr, " NUM:\tnumber of hands to be played\n");
	return -1;
}

int parser(int argc, const char * argv[]) {

    if (argc == 2 && !strcmp(argv[1], "-h")) {
        return usage(argv[0]);
    }

	// Argument parsing here
    const char* optv[] = {"-f", "-i", "-r", "-a", "-s"};
    int optc = 5;
    char target = 0;

    const char* ffile = "";
    long iseed = -1;
    const char* rfile = "";
    const char* afile = "";
	long anum = -1;
    bool sflag = false;

    // Search exclusively for -h option
    for (int i = 0; i < argc; i++) {
        if (argv[i] == "-h") return usage(argv[0]);
    }

    // Search for other options
    for (int i = 0; i < argc; i++) {
        const char* opt = argv[i];

        // Retrieve next argument
        // Need to rely on loop to avoid OutOfIndex access
        if (target != 0) {

            // Check if next argument is not an option
            for (int j = 0; j < optc; j++) {
                if (strcmp(opt, optv[j]) == 0) {
					if (target == 'A') {
						cerr << "Error: must specify number of hands when playing automatically." << endl;
					} else {
						cerr << argv[0] << ": option requires an argument -- '" << (char)tolower(target) << "'" << endl;
					}
                    return TERMINATE;
                }
            }

            // Save argument
            switch (target) {

                case 'f': {
					ffile = opt;
					target = 0;
					break;
				}

                case 'i': {
					char *pEnd;
			        iseed = strtol(opt, &pEnd, 10);
			        if ((*pEnd)||(iseed < 0)) {
						cout << "Error: SEED must be a non-negative integer." << endl;
						return TERMINATE;
					}
					target = 0;
					break;
				}

                case 'r': {
					rfile = opt;
					target = 0;
					break;
				}

                case 'a': {
					afile = opt;
					target = 'A'; // Special case for "-a" since it accepts two arguments
					break;
				}

				case 'A': {
					char *pEnd;
			        anum = strtol(opt, &pEnd, 10);
			        if ((*pEnd)||(anum <= 0)) {
						cout << "Error: NUM must be a natural number." << endl;
						return TERMINATE;
					}
					target = 0;
					break;
				}
            }
        }

        // Specify all valid options
        else {
            for (int j = 0; j < optc; j++) {
                if (strcmp(opt, optv[j]) == 0) {
                    // Special case for "-s", no need for argument parsing
                    if (strcmp(opt, "-s") == 0) {
                        if (sflag) {
                            cerr << "Error: too many -s options specified." << endl;
                            return TERMINATE;
                        }
                        sflag = true;

                    } else {
                        target = opt[1];

                        // Check if option already specified, excluding "-s"
                        bool manyOptionFlag = false;
                        switch (target) {
                            case 'f': if (strcmp(ffile, "") != 0) manyOptionFlag = true; break;
                            case 'r': if (strcmp(rfile, "") != 0) manyOptionFlag = true; break;
                            case 'a': if (strcmp(afile, "") != 0) manyOptionFlag = true; break;
                            case 'i': if (iseed != -1) manyOptionFlag = true; break;
                        }
                        if (manyOptionFlag) {
                            cerr << "Error: too many -" << target << " options specified." << endl;
                            return TERMINATE;
                        }

                        //cout << "[STATUS] Target: " << target << endl;
                    }
                    break;
                }
            }
        }
    }

    // Check if arguments are still needed
    if (target != 0) {
		if (target == 'A') {
			cerr << "Error: must specify number of hands when playing automatically." << endl;
		} else {
			cerr << argv[0] << ": option requires an argument -- '" << (char)tolower(target) << "'" << endl;
		}
		return TERMINATE;
    }
	if ((strcmp(ffile, "") != 0)&&(iseed != -1)) {
		cerr << "Error: cannot choose both file and random-based shoe." << endl;
		return TERMINATE;
	}
	if ((strcmp(rfile, "") != 0)&&(iseed == -1)) {
		cerr << "Error: recording is only available for random-based shoe." << endl;
		return TERMINATE;
	}
	if ((sflag)&&(strcmp(afile, "") == 0)) {
		cerr << "Error: silent mode is only available when playing automatically." << endl;
		return TERMINATE;
	}
	cout << endl;

    // Activate function based on flags (non-empty values)
    //cout << "[STATUS] ffile = " << ffile << endl;
    //cout << "[STATUS] iseed = " << iseed << endl;
    //cout << "[STATUS] rfile = " << rfile << endl;
    //cout << "[STATUS] afile = " << afile << endl;
    //cout << "[STATUS] anum = " << anum << endl;
	return 0;
}














void tester(int argc, const char* argv[], char expected[], int testNum) {
	cerr << "TEST #" << testNum << " ( ";
	for (int j = 0; j < argc; j++) {
		cerr << argv[j] << " ";
	}
	cerr << ")" << endl;
	cerr << "Expect: " << expected << endl;
	cerr << "Actual: "; parser(argc, argv); cerr << endl;
}

// Unit tests
int main() {

	int testNum = 1;
	{
		const char* argv[] = {"./a", "-f", "-i"};
		int argc = sizeof(argv)/4;
		char expected[] = "./a: option requires an argument -- 'f'";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./b", "-r"};
		int argc = sizeof(argv)/4;
		char expected[] = "./b: option requires an argument -- 'r'";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-f", "f"};
		int argc = sizeof(argv)/4;
		char expected[] = "";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-r", "r"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: recording is only available for random-based shoe.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-f", "r", "-i", "9"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: cannot choose both file and random-based shoe.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-s"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: silent mode is only available when playing automatically.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-a", "r", "-f", "f"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: must specify number of hands when playing automatically.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-a", "r", "4r", "-f", "f"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: NUM must be a natural number.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-a", "r", "-4", "-f", "f"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: NUM must be a natural number.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-i", "-1"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: SEED must be a non-negative integer.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-i", "1", "-i", "9"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: too many -i options specified.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-a", "f", "9", "-s", "-s"};
		int argc = sizeof(argv)/4;
		char expected[] = "Error: too many -s options specified.";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-i", "2", "-a", "f", "8", "-s", "-r", "f"};
		int argc = sizeof(argv)/4;
		char expected[] = "";
		tester(argc, argv, expected, testNum++);
	}
	{
		const char* argv[] = {"./a", "-i", "2", "-a", "f", "8", "-s", "-r", "f", "-h"};
		int argc = sizeof(argv)/4;
		char expected[] = "(help prompt)";
		tester(argc, argv, expected, testNum++);
	}
	return 0;
}
