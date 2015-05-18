Flask-consulate
===

Flask extension for [consulate](https://github.com/gmr/consulate)

This extension performs some application specific tasks, such as:

  1. Builtin retrying of connections to a single host, which may be useful
  when trying to resolve a consul cluster by hostname or behind a load balancer
  1. writes config values found in a namespaced consul kv store into `app.config`

