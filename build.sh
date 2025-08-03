#!/bin/sh

# clean cache
hexo clean

# generate article
hexo g

# show in localServer
hexo s

# update to github
hexo d

# create article
hexo new post 'article'
