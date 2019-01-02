# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.1] - 2019-01-02
### Changed
- Decrease longqueries server timeout to 5 min (from 1d)

## [1.2.0] - 2018-12-21
### Changed
- Add a curl based health check to validate that the socket it working
- Add haproxy.sock + socat to have a way to get statistics

## [1.1.0] - 2017-11-28
### Changed
- Set timeout to one day on events and logs entrypoints to allow streaming
- Increase maximum connection count to 512

### Added
- Separate dockerfile for debug-to-stdout variant

## [1.0.0] - 2017-11-13
Initial release based on haproxy 1.7
