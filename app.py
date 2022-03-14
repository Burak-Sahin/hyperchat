import datetime
import time
import redis
import threading

from flask import Flask, Response, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = "test"


class HyperServer:
    def __init__(self):
        """
        pub/sub based event stream using redis
        """
        pool = redis.ConnectionPool(host="localhost", port=6379, db=0)
        self.redis_cli = redis.Redis(connection_pool=pool, decode_responses=True)
        self.pubsub = self.redis_cli.pubsub()
        self.user_port = self._set_user()
        print(self.user_port)

    def join_room(self, user1, user2):
        """
        Enter a chat room if already exist
        If not, create one based on user names
        TODO: Handle group chats (probably in a separate method)
        :param user1: chat initiator
        :param user2: other chat participant
        :return:
        """
        room_name = f"{user1}-{user2}"
        alternative_room_name = f"{user2}-{user1}"
        for message in self.pubsub.listen():
            channel = message["channel"].decode(encoding="utf-8")
            if channel == room_name:
                return room_name
            elif channel == alternative_room_name:
                return alternative_room_name
        self.pubsub.subscribe(room_name)
        return room_name

    def send_message(self, room_name, user, message):
        now = datetime.datetime.now().replace(microsecond=0).time()
        self.redis_cli.publish(room_name, f"{now.isoformat()}, {user}, {message}")

    def get_messages(self):
        messages = []
        while True:
            message = self.pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                messages.append(message["data"])
            else:
                # TODO: Fix buggy behavior of first None message
                message = self.pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    messages.append(message["data"])
                else:
                    break
            time.sleep(0.001)
        return messages

    def disconnect(self):
        self.pubsub.close()
        self.redis_cli.close()

    def _next_port(self):
        """
        Calculates next port number
        TODO: Handle case when a chat participant is deleted
        :return: next available port number
        """
        ports = [8000]
        for k in self.redis_cli.scan_iter("user:*"):
            # 8000: default port
            port = int(self.redis_cli.get(k)) or 8000
            ports.append(port)
        return int(sorted(ports)[-1]) + 1

    def _set_user(self):
        port_num = self._next_port()
        user_name, user_port = f"user:{str(port_num)}", f"{str(port_num)}"
        self.redis_cli.set(user_name, user_port)
        return user_port

    def delete_users(self):
        for k in self.redis_cli.scan_iter("user:*"):
            self.redis_cli.delete(k)

    def get_user_list(self):
        user_dict = {}
        user_id = 1
        for k in self.redis_cli.scan_iter("user:*"):
            user_dict.update({f"user{user_id}": self.redis_cli.get(k).decode("utf-8")})
            user_id += 1
        return user_dict


hs = HyperServer()
# hs.send_message("8003", "u1", "My first message")
# hs.send_message("8003", "u2", "My second message")
# print(hs.get_user_list())

# msgs = hs.get_messages()
# for msg in msgs:
#     print(msg.decode('utf-8'))
# hs.disconnect()


@app.route("/", methods=["GET"])
def home():
    return render_template("users.html", users=hs.get_user_list())


@app.route("/<port>", methods=["GET", "POST"])
def message_room(port):
    # Sample chat room: localhost:8001/8003
    if request.method == "POST":
        message = request.form["message"]
        now = datetime.datetime.now().replace(microsecond=0).time()
        hs.send_message(hs.user_port, port, message)
        return Response(status=204)
    chat_name = f"from {hs.user_port} to {port}"
    hs.pubsub.subscribe(port)
    return render_template("message.html", room_name=chat_name)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=hs.user_port, debug=True)
