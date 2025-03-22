@echo off
cd /d %~dp0
python generate_service.py install
python generate_service.py start