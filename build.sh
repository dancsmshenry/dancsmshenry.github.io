#!/bin/sh

hexo clean
hexo g

# show in local
hexo s

# update in github
hexo d
