#! /usr/bin/python

import argparse, random, sys

# Generating a normal distribution, since that's typical for grades.  Students
# usually stay in about the same score region.
def generate_scores(quantity, max_score=100, overall_mean_score=None, 
                    overall_score_std_dev=None, mean_improvement=0, 
                    std_dev_improvement=None):
    if overall_mean_score is None:
        overall_mean_score = max_score * 0.75
    if overall_score_std_dev is None:
        overall_score_std_dev = max_score / 5
    if std_dev_improvement is None:
        std_dev_improvement = max_score / 10

    last_score = None
    for i in xrange(quantity):
        if last_score is None:
            last_score = random\
                             .normalvariate(overall_mean_score, 
                                            overall_score_std_dev)
        else:
            last_score += random.normalvariate(0, 10)
        last_score = int(max(0, min(last_score, max_score)))
        yield last_score

class AutoshuffleList(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.current_index = 0

    def __iter__(self):
        while True:
            yield self[self.current_index]
            self.current_index = (self.current_index + 1) % len(self)
            if self.current_index == 0:
                random.shuffle(self)

# This is an object instead of naive strings in Student because names are 
# complicated and in the long run it's only a matter of time until the
# simple version doesn't work.  This particular name is representative
# of the western Europe/American style of [Given Name] [Paternal Name]
class Name(object):
    def __init__(self, first, last):
        self.first = first
        self.last = last

    def __repr__(self):
        return "{0} {1}".format(self.first, self.last)

class NameGenerator(object):
    def __init__(self, first_names, last_names):
        self.first_name = iter(first_names)
        self.last_name = iter(last_names)
        self.max_names_generated = float('inf')

    def generate_name(self):
        return Name(self.first_name.next(),
                    self.last_name.next())

    def generate_names(self, number_of_names):
        names_generated = 0
        while (names_generated < number_of_names):
            names_generated += 1
            yield self.generate_name()

class UniqueNameGenerator(NameGenerator):
    def __init__(self, first_names, last_names, *args):
        NameGenerator.__init__(self, first_names, last_names, *args)
        self.generated_names = set()
        self.max_names_generated = len(first_names) * len(last_names)

    def generate_names(self, number_of_names):
        while (len(self.generated_names) < number_of_names):
            new_name = self.generate_name()
            while str(new_name) in self.generated_names:
                new_name = self.generate_name()
            self.generated_names.add(str(new_name))
            yield new_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Create test data for challenge #168: Test Data.')

    parser.add_argument('first_name_file',
                        metavar='FILE OF FIRST NAMES',
                        help='file containing first names to use')
    parser.add_argument('last_name_file',
                        metavar='FILE OF LAST NAMES',
                        help='file containing last names to use')
    parser.add_argument('-m',
                        '--mean-score',
                        action='store',
                        type=int,
                        dest='mean_score',
                        help='The mean score across all students')
    parser.add_argument('-sd',
                        '--standard-deviation',
                        action='store',
                        type=int,
                        dest='std_dev',
                        help='The standard deviation of scores across all students.')
    parser.add_argument('-im',
                        '--mean-improvement',
                        action='store',
                        type=int,
                        default=0,
                        dest='mean_improvement',
                        help='The average amount student scores rise between scores.')
    parser.add_argument('-isd',
                        '--standard-deviation-improvement',
                        action='store',
                        type=int,
                        dest='std_dev_improvement',
                        help='The standard deviation of the rise between scores.')
    parser.add_argument('-x',
                        '--max-score',
                        action='store',
                        type=int,
                        default=100,
                        dest='maximum_score',
                        help='The maximum score.')
    parser.add_argument('-n',
                        '--number',
                        action='store',
                        type=int,
                        default=10,
                        dest='number_of_names',
                        help='How many names to generate.')
    parser.add_argument('-o',
                        '--output',
                        action='store',
                        default=None,
                        dest='output',
                        help='Output file to use.  If not provided, uses stdout.')
    parser.add_argument('-t',
                        '--scores',
                        action='store',
                        type=int,
                        default=5,
                        dest='number_of_scores',
                        help='How many scores to generate per student.')
    parser.add_argument('-u',
                        '--require_unique',
                        action='store_true',
                        dest='require_unique_names',
                        help='Require unique names')

    args = parser.parse_args()

    with open(args.first_name_file) as first_name_file:
        with open(args.last_name_file) as last_name_file:
           with (open(args.output, 'w') 
                  if args.output is not None else sys.stdout) \
                 as outfile:
                return_code = 0

                # We shuffle these before the constructor since it's good form for
                # testability; this allows us to push in something that isn't 
                # shuffled and get back something predictable
                first_names = AutoshuffleList(
                                [stripped for stripped in 
                                 [line.strip() for line in first_name_file] 
                                 if stripped != ''])
                random.shuffle(first_names)
                last_names = AutoshuffleList(
                                [stripped for stripped in 
                                 [line.strip() for line in last_name_file] 
                                 if stripped != ''])
                random.shuffle(last_names)

                if args.require_unique_names:
                    name_generator = UniqueNameGenerator(first_names, last_names)
                else:
                    name_generator = NameGenerator(first_names, last_names)

                if args.number_of_names > name_generator.max_names_generated:
                    print >> sys.stderr, "Not enough possible combinations of", \
                                         "names to guarantee uniqueness,", \
                                         "generating {} names"\
                                         .format(name_generator.max_names_generated)
                    return_code = 1

                for name in name_generator.generate_names(args.number_of_names):
                    outfile.write("{0} , {1} {2}\n"\
                                  .format(name.last, name.first,
                                  ' '.join([str(score)
                                            for score
                                            in generate_scores(
                                                args.number_of_scores,
                                                max_score=args.maximum_score,
                                                overall_mean_score=args.mean_score,
                                                overall_score_std_dev=args.std_dev,
                                                mean_improvement=args.mean_improvement,
                                                std_dev_improvement=args.std_dev_improvement)])))

                exit(return_code)
