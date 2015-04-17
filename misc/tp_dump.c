#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <getopt.h>

#include "tp.h"
#include "tp_transcode.h"

void
usage(char **argv)
{
	printf(
			"USAGE: %s [in file name] -- stdin if empty\n\n"
			"Warning!\n"
			"This program is not stream based.\n"
			"Use this program only for fixed size tarantool protocol messages\n"
			"\n",
			argv[0]
	);
	exit(0);
}

int
main(int argc, char ** argv)
{
	FILE *in = stdin;

	int c;
	static struct option long_options[] = {
		{"in-file", required_argument, 0, 'i'},
		{0, 0, 0, 0}
	};
	int index = 0;
	while ((c = getopt_long(argc, argv, "ih:", long_options, &index)) != -1){
		switch(c){
		case 'i':
			in = fopen(optarg, "r");
			if (in == NULL) {
				fprintf(stderr, "Failed to open file '%s', error '%s'\n",
						optarg, strerror(errno));
				exit(2);
			}
			break;
		case 'h':
			usage(argv);
		}
	}

	char err[255], obuf[1024*2], ibuf[1024*2];
	memset(err, 0, sizeof(err));
	memset(obuf, 0, sizeof(obuf));
	memset(ibuf, 0, sizeof(ibuf));

	tp_transcode_t tc;
	if (tp_transcode_init(&tc, obuf, sizeof(obuf) - 1, TP_TO_JSON)
            == TP_TRANSCODE_ERROR)
    {
		fprintf(stderr, "Failed to initialize transcode\n");
		return 2;
	}

	size_t size = 0;
	for (size_t rd = 0;;) {
		size += rd = fread((void *)&ibuf[size], 1, sizeof(ibuf) - size, in);
		if (rd == 0) {
			if (!feof(in)) {
				fprintf(stderr, "Failed to read file, error: '%s'\n",
						strerror(ferror(in)));
				return 2;
			}
			break;
		}
	}

	if (tp_transcode(&tc, ibuf, size) == TP_TRANSCODE_ERROR) {
		fprintf(stderr, "Failed to transcode , msg: '%s'\n", tc.errmsg);
		return 2;
	}

	size_t complete_msg_size = 0;
	if (tp_transcode_complete(&tc, &complete_msg_size) == TP_TRANSCODE_ERROR) {
		fprintf(stderr, "Failed to complete transcode, msg '%s'\n", tc.errmsg);
		return 2;
	}

	printf("Dump: '%.*s'\n", (int)complete_msg_size, obuf);

	return 0;
}