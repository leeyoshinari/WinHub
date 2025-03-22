@echo off
cd /d %~dp0
python generate_service.py remove
python generate_service.py stop