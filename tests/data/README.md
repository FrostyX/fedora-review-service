# Test data

I downloaded all test messages like this:

```bash
ID="75f5e27d-6409-4481-8396-25ef69ed8177"
http --json get https://apps.fedoraproject.org/datagrepper/v2/id id=="$ID" is_raw==true size==extra-large |jq
```

You can preview messages also online, e.g.

https://apps.fedoraproject.org/datagrepper/v2/id?id=75f5e27d-6409-4481-8396-25ef69ed8177


If you want to view a message but you don't know its ID, you can use
the following script to list interesting messages from the last couple
of hours.

```bash
python query-fedora-messages.py
```
