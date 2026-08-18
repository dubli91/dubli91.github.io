---
date: 2022-09-05
categories:
  - CKA
tags:
  - CKA
  - Kubernetes
slug: cka-exam-review
---

# CKA Exam Review

I took the CKA exam last Saturday and got the passing notification the next day, on Sunday. I'd like to briefly share how I prepared, the difficulties I ran into along the way, and my overall impressions.

## 1. Why I Took the Exam / Where I Started From
I normally develop API servers with Spring Boot. Occasionally I use Python too. I operate API servers on AWS, though I've never provisioned AWS resources from scratch myself. I'm comfortable with the shell, but my Linux OS knowledge isn't deep.

At work, I wasn't using k8s at all. I had zero Kubernetes (k8s, hereafter) knowledge, and my understanding of Docker went no further than the vague notion that it was some container-based technology. Then a new assignment landed on me where all the code ran on top of every CI/CD tool imaginable, k8s included. After getting GitHub access for the first time and googling code with file extensions I'd never seen in my life, I hit the limits of trying to understand the code through fragmentary knowledge.

Eventually I concluded I needed to study the fundamentals through online courses or books, and some fellow developers around me recommended an exam called the CKA. It's a certification exam offered by the Linux Foundation, and the knowledge it demands seemed closely tied to real-world work. So I started preparing in earnest about two months before the exam. Even starting from that level of knowledge, I earned the certification in about two months while working my day job.

## 2. Study Materials / References

Below are the courses, references, and k8s environments I used while studying. Note that the courses use auto-generated subtitles, so words often come out garbled — keep that in mind.

### 1) Courses
- [Certified Kubernetes Administrator (CKA) with Practice Tests](https://www.udemy.com/share/101WmE/)

This is "that course" — the one that shows up in every CKA pass report. It covers everything from the fundamentals needed for the CKA exam and provides all the practice environments and practice problems too. If you time a sale, you can apparently get it for under 50,000 KRW (I took it for free with a Udemy license provided by my company). This course alone is enough to pass.

- [Kubernetes for the Absolute Beginners - Hands-on](https://www.udemy.com/share/1013LO/)

If the course above feels a bit intimidating, starting k8s with this one — by the same instructor — is also a good option. It's mostly focused on writing yaml, but it was good for building the basic concepts.

### 2) References

- [Kubernetes official documentation](https://kubernetes.io/docs/home/)

Effectively the only reference you're allowed to consult during the exam. Even when solving practice problems day to day, it's good to build the habit of searching the docs by keyword before looking at hints or solutions.

- [Managing Kubernetes Objects Using Imperative Commands](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/imperative-command/)

Solving 17 problems in 2 hours leaves you pressed for time. Rather than hand-writing yaml files one by one, you're better off getting comfortable with the run, create, and expose commands. If you can't remember a command's options during the exam, use the -h option to check the help text.

- Various blog reviews / Chinese blogs

Only consult review posts written after the exam switched to the PSI-based format. Also — something I learned after the exam — Chinese blogs often contain the actual exam questions and solutions verbatim. When I googled a few keywords while reviewing after the exam, I personally confirmed that blogs written in Chinese really did have the exact questions that appeared on my exam, along with their solutions.


### 3) Practice Environments
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)

It turns your own computer into a k8s cluster consisting of a single master node. Most k8s hands-on practice can be done with this, but the downside is that you can't do exercises requiring multiple nodes (like building a cluster with kubeadm). Also, I often ran into Permission denied errors when trying to inspect the k8s config files in detail.

- [Killercoda](https://killercoda.com/)

A site I only discovered after taking the exam. It provides an online environment for k8s hands-on practice. I was even surprised by how fast it is.

Search for the topic you want to practice and it builds and serves up a matching environment (like ingress). You'll end up using Killer.sh for the exam anyway, so it seems like a good idea to use both together while you're at it.

## 3. Finding an Exam Location
The thing that worried me most about the exam was the location. Obviously no one can be around you, but also there can't be any text stuck on the walls, there must be nothing on or under the desk, and above all it has to be quiet.

My home is cluttered and has bookshelves crammed in everywhere, so I had a lot of trouble finding a suitable spot. In the end I booked a study room, and I set up the space with the following in mind:

- A room fully enclosed by solid walls
- A door that locks (to keep people from walking in), with no window in the door (frosted glass included)
- Not too noisy (someone in the next room kept banging on a whiteboard, which drove me crazy)
- Good Wi-Fi reception, with wired LAN available if needed
- No artwork on the walls and minimal posted notices

I searched for nearly a week before finding a place that met all of these. I did a scouting visit the week before the exam, was satisfied, and used the same place on exam day.

The last item was the tricky part, though — I just brought A4 paper and tape and covered up all the notices (the Wi-Fi password, checkout instructions, and so on), and the proctor let it pass without comment.

Definitely do a scouting visit to check the Wi-Fi and the rest of the exam environment, and on the day itself bring an Ethernet adapter and a charger.

For reference, the place where I took my exam is [here](https://thegoalstudy.modoo.at/).

## 4. Don't panic, don't panic, don't panic.

This is a line from the Certification Tips section at the end of the Certified Kubernetes Administrator (CKA) with Practice Tests course, and it helped me a lot. Think of it as an exam where you only need to clear 66 out of 100 points, and take it easy.
