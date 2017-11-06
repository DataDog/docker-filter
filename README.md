# Datadog Docker socket filter
Filtering proxy for a read-only access to the Docker socket, based on [HAProxy](https://www.haproxy.org/).

[![CircleCI](https://circleci.com/gh/DataDog/docker-filter/tree/master.svg?style=svg)](https://circleci.com/gh/DataDog/docker-filter/tree/master)

## Quick start

See [sample docker-compose file](example.compose).

## Why?

The Docker engine does not currently offer any monitoring interface (to list and inspect containers / images / volumes) other than the management socket. This API is pretty stable and allows our agents to get reliable data, but it comes with a severe security risk: all commands sent to it are executed with root privileges.  An attacker could use that as a privilege escalation mechanism.

The [authorization subsystem](https://docs.docker.com/engine/extend/plugins_authorization/) tries to solve this issue by enabling a rule-based authorization workflow, but it has several shortcomings:

- it requires SSL client certificate authentication, which is currently not supported on the unix socket, potentially breaking orchestrators and third party software assuming access to `/var/run/docker.sock`
- it is not self-contained in the Docker engine, but requires the sysadmin to install and configure a third-party software
- if no certificate chain is already setup, creating one for that use case is a big hurdle
 
This is why this container aims at providing a simpler solution.

## How?

The Docker management API is a standard [HTTP REST API](https://docs.docker.com/engine/api/latest/), which can be filtered through a filtering HTTP proxy. This container uses HAProxy to provide a read-only access to the API, via a socket created in the shared volume mounted in `/safe-docker`. Our [provided configuration](docker/haproxy.cfg):

- only allows `GET`/`HEAD` requests, as all requests that modify the state of an object are either `POST`, `PUT` or `DELETE`
- passes URLs through a [whitelist](docker/url-whitelist.lst) to forbid access to endpoints that might be exploited to escalade access (attach via a websocket) or enable DoS attacks (disk/network intensive read-only operations)

The remaining endpoints are deemed safe for use and are accessible on the safe socket. This socket can then be exposed to monitoring software.