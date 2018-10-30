# Property Wrapper
## Overview
This library provides a simple interface for creating class wrappers for subscriptable data stuctures.  It makes it possible to easily add properties pointing to values within the underlying data in order to reference them with dot notation.  
## Use Cases
### Abstracting Out Structure
The main purpose of a property wrapper is to allow programs to work with data without having to know the data's underlying structure.  Keeping the structure of data abstract is useful for two reasons:
#### Easier Access
You may want to make it easier to access the values you care about in a data structure.  This can be useful when you need to manipulate data that has a predetermined structure.  If your data stores a value at the path `data['foo']['bar']['baz']` and you simply want to refer to this value as `data.baz`, you can create a property for it and never have to store the lookup path anywhere else.
#### Safety/Compatibility
Let's say you've written a program that manipulates complex data in a predetermined structure, and you don't use a property wrapper.  Throughout your program, you use subscript notation to access values in the data.  Then, the structure of the data or the value of a key changes, perhaps because you upgrade to a newer version of an API.  You now have to go through your code by hand and change how you access values in the data.  With a property wrapper, you could prevent this situation and only have to change the lookup path once.
### Flexible Serialization
Another use for property wrappers is easily and safely creating classes that are serializable in a flexible manner (rather than just outputting the `__dict__` attribute).  For example, you may want a class to keep track of attributes that shouldn't be reflected in the underlying data.  In such cases, you can add normal class attributes in the wrapper's `__init__` method in addition to attributes that point to values in the underlying data.
## Example
This example shows how a property wrapper can be used to work with JSON representing a GCE instance.  It demonstrates both of the use cases described above.

Here's how GCE stores data to represent an instance:
```json
{
  "kind": "",
  "id": "",
  "creationTimestamp": "",
  "name": "",
  "tags": {
    "items": [],
    "fingerprint": ""
  },
  "machineType": "",
  "status": "",
  "zone": "",
  "networkInterfaces": [
    {
      "kind": "",
      "network": "",
      "subnetwork": "",
      "networkIP": "",
      "name": "",
      "accessConfigs": [
        {
          "kind": "",
          "type": "",
          "name": "",
          "natIP": ""
        }
      ],
      "fingerprint": ""
    }
  ],
  "disks": [
    {
      "kind": "",
      "type": "",
      "mode": "",
      "source": "",
      "deviceName": "",
      "index": 0,
      "boot": false,
      "autoDelete": false,
      "licenses": [],
      "interface": ""
    }
  ],
  "metadata": {
    "kind": "",
    "fingerprint": ""
  },
  "selfLink": "",
  "scheduling": {
    "onHostMaintenance": "",
    "automaticRestart": false,
    "preemptible": false
  },
  "cpuPlatform": "",
  "labels": {
    "department": "",
    "expiration": "",
    "owner": "",
    "module_type": ""
  },
  "labelFingerprint": "",
  "startRestricted": false,
  "deletionProtection": false
}
```
You probably shouldn't be navigating that huge chunk of JSON every time you want to access a value.  Instead, create a property wrapper:
```python
class Instance(dict, PropertyWrapper, props={
    'name': prop(['name']),
    'owner': prop(['labels', 'owner']),
    'department': prop(['labels', 'department']),
    'preemptible': prop(['scheduling', 'preemptible']),
    'machine_type': prop(['machineType']),
    'status': prop(['status']),
    'self_link': prop(['selfLink']),
    'expiration': prop(['labels', 'expiration']),
    'module': prop(['labels', 'module_type']),
}):

    def __init__(self, data, project, zone, disks):
        super().__init__(data)
        # The project in which the instance resides
        self.project = project
        # The simple name of the zone, as opposed to the giant URL 
        # stored in the instance data
        self.zone = zone
        # The full data of the disks, as opposed to the truncated 
        # version stored in the instance data
        self.disks = disks

```
At the top of the class definition is a dictionary of properties linked to values in the underlying data.  Each key represents the property's name, and the `prop` function creates a spec for a property.  It takes in a list of keys representing the lookup path, as well as four optional arguments: `fget`, `fset`, `fdel`, and `doc`.  Setting `fget`, `fset`, or `fdel` to `False` will prevent the property from being retrieved, set, or deleted, respectively.  By default, all are enabled.  You can also pass in custom methods for getting, setting, and deleting a property, but this is generally not recommended.

The class's `__init__` method declares three normal attributes that are useful within a program, but will not be reflected in the underlying data.

By using the property wrapper in situations such as this, it's possible to serialize and deserialize JSON, manipulate its values, add useful information, and preserve the original data structure.