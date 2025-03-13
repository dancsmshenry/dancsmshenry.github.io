#!/bin/sh

hexo clean
hexo g

# show in localServer
hexo s

# update to github
hexo d

# create article
hexo new post 'article'