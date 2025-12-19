@echo off
git reset
git checkout
git reset --hard HEAD
git clean -fdx
cmd /K