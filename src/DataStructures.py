# uses Linked List structure
class Queue:
    class Node:
        def __init__(self, data):
            self.data = data
            self.next = None

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, data):
        node = Queue.Node(data)

        if not self.head:
            self.head = node
            self.tail = node

        else:
            self.tail.next = node
            self.tail = node

        self.size += 1

        return

    def dequeue(self):

        if not self.tail:
            raise Exception("Cannot dequeue from an empty queue")

        data = self.head.data
        self.head = self.head.next
        self.size -= 1

        return data

    def getSize(self):
        return self.size

    def isEmpty(self):
        return self.size == 0


class CircularLinkedList:
    class Node:
        def __init__(self, data):
            self.data = data
            self.next = None

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insertHead(self, data):
        node = CircularLinkedList.Node(data)
        self.length += 1
        if not self.head:
            self.head = node
            self.tail = node

        else:
            temp = self.head
            node.next = temp
            self.head = node

        self.tail.next = node

    def insertTail(self, data):
        node = CircularLinkedList.Node(data)
        self.length += 1
        if not self.tail:
            self.head = node
            self.tail = node
            self.tail.next = node

        else:
            node.next = self.tail.next
            self.tail.next = node
            self.tail = node

    def getList(self):
        dataList = []

        if not self.head:
            return dataList

        else:

            current = self.head

            while True:

                dataList.append(current.data)

                current = current.next

                if current == self.head:
                    break

            return dataList

    def getSet(self):
        dataSet = set()

        if not self.head:
            return dataSet

        else:
            current = self.head

            while True:
                dataSet.add(current.data)
                current = current.next
                if current == self.head:
                    break

            return dataSet

    def search(self, target, start=None, end=None, key=lambda x: x):
        if not self.head:
            return None
        if not start:
            current = self.head
        else:
            current = start

        if not end:
            end = start

        while True:

            if key(current.data) == target:
                return current

            else:
                current = current.next
                if current == end:
                    return None

    def deleteNode(self, target, key=lambda x: x):
        if not self.head:
            return False

        if key(self.head.data) == target:

            if self.head.next == self.head:
                self.head = None
                self.tail = None
                self.length -= 1
                return True

            else:
                temp = self.head
                self.tail.next = self.head.next
                self.head = temp.next
                self.length -= 1
                return True

        prev = self.head
        current = prev.next

        while current != self.head:
            if key(current.data) == target:
                prev.next = current.next
                self.length -= 1
                return True

            else:
                prev = prev.next
                current = current.next

        return False

    def __repr__(self):
        return ", ".join(self.getList())
