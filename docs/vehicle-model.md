# Vehicle Edge Computing Model

## Tractor Edge Cluster Architecture

```text
                    CLOUD
                      │
                Internet / AWS
                      │
                      ▼
                ┌───────────┐
                │    NUC    │
                │  x86_64   │
                │   Edge    │
                │  Manager  │
                └─────┬─────┘
                      │
             Docker Swarm / Network
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌────────┐    ┌────────┐    ┌────────┐
   │ Xavier │    │ Xavier │    │ Xavier │
   │ ARM64  │    │ ARM64  │    │ ARM64  │
   └────────┘    └────────┘    └────────┘
        │
        └────────── Xavier #4
```

## NUC (Intel x86_64 Edge Manager)

- x86_64
- More powerful compute
- Runs Linux
- Can run Docker/Kubernetes/Swarm
- Acts as a central edge compute/management node
- Can communicate with the cloud

## Xavier Nodes (NVIDIA Jetson ARM64)

- ARM64
- NVIDIA Jetson Xavier-class hardware
- Local compute at the edge
- Can run Linux + containers
- Can process data from vehicle systems/sensors
- Can perform AI/vision workloads

## Summary

So the tractor itself is essentially an edge computing cluster.

---

## Platform Use Case

> "I want to build a platform that manages heterogeneous edge fleets."

### EaaS Platform Architecture

```text
                    EaaS Platform
                         │
                  ┌──────┴──────┐
                  │             │
                Cloud        Device Fleet
                                │
              ┌─────────────────┼────────────────┐
              │                 │                │
           NUC x86           Jetson ARM64     ESP32
           Linux             Linux            Firmware
              │                 │                │
           Docker            Docker           OTA
           OTA               OTA
           Monitoring        Monitoring
           Remote Ops        Remote Ops
```

## IoT Devices in the Tractor

Things such as:

- Sensors — temperature, pressure, position, speed, etc.
- Vehicle ECUs/controllers
- GPS/GNSS modules
- Battery/BMS controllers
- Motor/inverter controllers
- CAN-connected devices
- Other embedded controllers that collect data or control physical components

These are closer to what we normally call IoT/connected devices.

## The NUC as Edge Device

The NUC is an Edge Device.

It is much more than a simple sensor:

```text
NUC
 ├── Linux
 ├── Docker
 ├── Edge applications
 ├── Networking
 ├── Data processing
 ├── Device communication
 └── Cloud communication
```

It can collect data from many devices, process it locally, and communicate with AWS.

## Xavier Boards as Edge Devices

The 4 Xavier boards are also primarily Edge Devices. Because they have substantial compute capability and can run applications locally:

```text
Xavier
 ├── Linux
 ├── Containers
 ├── AI/ML workloads
 ├── Data processing
 ├── Vehicle communication
 └── Local decision making
```

They can also technically be IoT devices because they are connected devices communicating with a network/cloud. But from an architecture perspective, I'd call them edge compute nodes.

## Hierarchy: Device Classification

| Component | Classification | Example Responsibility |
|-----------|-----------------|------------------------|
| Sensor | IoT/embedded device | Measure temperature |
| ECU | IoT/embedded device | Control motor/system |
| GPS module | IoT device | Location |
| NUC | Edge device | Aggregate/process/manage |
| Xavier | Edge device | AI/compute/process |
| AWS | Cloud | Fleet management/data |

## Platform Vision: From IoT to Edge to Cloud

Your EaaS vision can cover both layers:

```text
IoT devices → Edge devices → Cloud
```

And this is actually a strong reason to make your platform hardware-agnostic. Your experience wasn't just with individual IoT sensors—you worked with a heterogeneous edge fleet containing x86_64 and ARM64 compute nodes plus vehicle-level connected devices.