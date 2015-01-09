#
# Depends on a patch to the python circleci tool:
#    https://github.com/qba73/circleclient/pull/4
#
# Run on command line like so:
#    CIRCLECI_API_TOKEN="" CIRCLECI_REPO_ORG="" CIRCLECI_REPO_NAME="" CIRCLECI_BRANCH="" python circletimes.py
#

from circleclient import circleclient
import datetime
from matplotlib import pyplot, ticker
import numpy
import os


def get_builds():
    TOKEN = os.environ['CIRCLECI_API_TOKEN']
    REPO_ORG = os.environ['CIRCLECI_REPO_ORG']
    REPO_NAME = os.environ['CIRCLECI_REPO_NAME']
    BRANCH = os.environ['CIRCLECI_BRANCH']

    client = circleclient.CircleClient(TOKEN)
    builds = client.build.recent(REPO_ORG, REPO_NAME,
                                 branch=BRANCH,
                                 limit=100,
                                 filter="successful")
    builds.extend(client.build.recent(REPO_ORG, REPO_NAME,
                                      branch=BRANCH,
                                      limit=100,
                                      filter="successful",
                                      offset=100))
    builds.extend(client.build.recent(REPO_ORG, REPO_NAME,
                                      branch=BRANCH,
                                      limit=100,
                                      filter="successful",
                                      offset=200))
    builds.extend(client.build.recent(REPO_ORG, REPO_NAME,
                                      branch=BRANCH,
                                      limit=100,
                                      filter="successful",
                                      offset=300))
    return builds

def create_dataset(builds):
    xseries = []
    buildtimes = []
    for build in builds:
        buildtimes.append(build["build_time_millis"]/1000.0/60.0)
        #2015-01-08T23:45:35.452Z
        format = "%Y-%m-%dT%H:%M:%S.%fZ"
        date_object = datetime.datetime.strptime(build["start_time"], format)
        xseries.append(date_object)
    return numpy.array(buildtimes), numpy.array(xseries)

def moving_average(values, window):
    weigths = numpy.repeat(1.0, window)/window
    # numpy array
    return numpy.convolve(values, weigths, 'valid')

def plot(buildtimes, xseries, moving_avg):
    pyplot.plot(xseries, buildtimes, 'k.')
    pyplot.plot(xseries[:len(moving_avg)], moving_avg, 'r')
    pyplot.xlim(min(xseries), max(xseries))
    pyplot.ylim(min(buildtimes)-1, max(buildtimes)+1)
    pyplot.ylabel("Build time in minutes")
    pyplot.grid(True)

    pyplot.gcf().autofmt_xdate()
    import matplotlib.dates as mdates
    pyplot.gca().fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    pyplot.title("Time in minutes of successful builds with moving average")
    pyplot.show()

def create_xseries(dataset):
    return range(1, len(dataset))

if __name__ == "__main__":
    builds = get_builds()
    buildtimes, xseries = create_dataset(builds)
    moving_avg = moving_average(buildtimes, 10)
    plot(buildtimes, xseries, moving_avg)
