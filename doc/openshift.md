# OpenShift deployment

At this time, the `fedora-review-service` is deployed in Fedora
CommuniShift.

- Dashboard: https://console-openshift-console.apps.fedora.cj14.p1.openshiftapps.com/
- Documentation: https://docs.fedoraproject.org/en-US/infra/ocp4/sop_communishift/


## Tools

For some reason, in the Fedora repositories, there is an outdated
(version 3.x) `oc` command (the `origin-clients` package). You might
need to install it like this

https://docs.okd.io/latest/cli_reference/openshift_cli/getting-started-cli.html


## Login

First, log in using the OpenShift dashboard URL, then click your name
in the top-right and "Copy login command". Display token and run the
`oc` command.

```bash
oc login --token=... --server=https://api.fedora.cj14.p1.openshiftapps.com:6443
```

## Deploy

Our OpenShift deployment uses a pre-built container from
[quay.io/jkadlcik/fedora-review-service][quay-repo].

Before rebuilding the container, it is probably a good idea to do

```
git stash
git checkout main
git pull --rebase
```

To rebuild the container image to use the most recent code, do

```
docker-compose build
docker-compose push
```

If a Kubernetes/OpenShift configuration change needs to be applied,
run the following command. Otherwise you can skip it.

```
oc apply -f openshift/fedora-review-service.yaml
```

To kill the current deployment and start a fresh, up-to-date
container, run

```
oc rollout restart deploy/fedora-review-service-fedmsg
```



[quay-repo]: https://quay.io/repository/jkadlcik/fedora-review-service
