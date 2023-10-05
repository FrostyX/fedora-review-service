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


## Permissions

To be able to access the OpenShift project please ping fedora-infra to
add you to [communishift][group1] group and @FrostyX, to add you to
[communishift-fedora-review-service][group2] group.


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

To rebuild the container image to use the most recent code, and
publish it to [quay.io][quay-repo], do

```
docker-compose build
docker-compose push
```

Make sure you are using the correct OpenShift project

```
oc project communishift-fedora-review-service
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

Make sure the service is up and running

```
oc logs -f deploy/fedora-review-service-fedmsg
# or
oc rsh deploy/fedora-review-service-fedmsg
```


## Tokens

At this moment, the production auth tokens for Bugzilla and Copr, are
stored only on a persistent volume in the OpenShift. It is mounted as
`/persistent` to the running container. In case they expire, please
open a remote shell to the container, and manually update themm.

Also, at this moment, the service uses my (@FrostyX) personal token
for Copr and therefore builds are submitted under my username. For
Bugzilla, we use the [fedora-review-bot][fedora-review-bot] account.


[quay-repo]: https://quay.io/repository/jkadlcik/fedora-review-service
[group1]: https://accounts.fedoraproject.org/group/communishift/
[group2]: https://accounts.fedoraproject.org/group/communishift-fedora-review-service/
[fedora-review-bot]: https://fedoraproject.org/wiki/User:Fedora-review-bot
