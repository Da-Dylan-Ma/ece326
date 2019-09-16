#include <cstdio>
#include <cstring>
//#include <unistd.h> // <unistd> original

#include <unordered_set>
#include <iostream>
//#include <string>
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

int main(int argc, const char * argv[]) {
    if (argc == 2 && !strcmp(argv[1], "-h")) {
        return usage(argv[0]);
    }

	// Argument parsing here
    const char* optv[] = {"-f", "-i", "-r", "-a", "-s"};
    int optc = 5;
    char target = 0;
    const char* fvalue = "";
    const char* ivalue = "";
    const char* rvalue = "";
    const char* avalue = "";
    bool sflag = false;

    // Search exclusively for -h option
    for (int i = 0; i < argc; i++) {
        if (argv[i] == "-h") return usage(argv[0]);
    }

    // TODO: Multiple same options
    // Search for other options
    for (int i = 0; i < argc; i++) {
        const char* opt = argv[i];
        cout << "[STATUS] Processing: " << opt << endl;

        // Retrieve next argument
        // Need to rely on loop to avoid OutOfIndex access
        if (target != 0) {
            cout << "[STATUS] Checking args" << endl;

            // Check if next argument is not an option
            for (int j = 0; j < optc; j++) {
                if (strcmp(opt, optv[j]) == 0) {
                    cerr << "./asst1: option requires an argument -- '" << target << "'" << endl;
                    return TERMINATE;
                }
            }

            // Save argument
            switch (target) {
                case 'f': fvalue = opt; break;
                case 'i': ivalue = opt; break;
                case 'r': rvalue = opt; break;
                case 'a': avalue = opt; break;
            }
            target = 0;
        }

        // Specify all valid options
        else {
            for (int j = 0; j < optc; j++) {
                if (strcmp(opt, optv[j]) == 0) {
                    // Differentiate between argument-requiring options
                    if (strcmp(opt, "-s") == 0) {
                        if (sflag) {
                            cerr << "Error: too many -s options specified." << endl;
                            return TERMINATE;
                        }
                        sflag = true;

                    } else {
                        target = opt[1];
                        // Check if option already specified, excluding "-s"
                        const char* tvalue;
                        switch (target) {
                            case 'f': tvalue = fvalue; break;
                            case 'i': tvalue = ivalue; break;
                            case 'r': tvalue = rvalue; break;
                            case 'a': tvalue = avalue; break;
                        }
                        if (strcmp(tvalue, "") != 0) {
                            cerr << "Error: too many -" << target << " options specified." << endl;
                            return TERMINATE;
                        }

                        cout << "[STATUS] Target: " << target << endl;
                    }
                    break;
                }
            }
        }
    }

    // Check if arguments are still needed
    if (target != 0) {
        cerr << "./asst1: option requires an argument -- '" << target << "'" << endl;
        return TERMINATE;
    }

    // Activate function based on flags (non-empty values)
    cout << "[STATUS] fvalue = " << fvalue << endl;
    cout << "[STATUS] ivalue = " << ivalue << endl;
    cout << "[STATUS] rvalue = " << rvalue << endl;
    cout << "[STATUS] avalue = " << avalue << endl;

    // TODO: Add restrictions
    // Check if svalue is non-negative integer
    /*if (strcmp(svalue, "") != 0) {
        char *pEnd;
        long ivalue_int = strtol(svalue, &pEnd, 10);
        if (*pEnd) {

        }

    }*/

	return 0;
}
