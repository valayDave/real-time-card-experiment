import os
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from metaflow import S3, metaflow_config, profile, Task, namespace
from metaflow.cards import get_cards

TASK_CACHE = {}


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            _, path = self.path.split("/", 1)
            try:
                prefix, suffix = path.split("/", 1)
            except:
                prefix = path
                suffix = None
        except:
            prefix = None
        if prefix in self.ROUTES:
            self.ROUTES[prefix](self, suffix)
        else:
            with open("index.html", "rb") as f:
                self._response(f.read())

    def get_runinfo(self, suffix):
        latest = find_latest_run()
        if latest:
            flow, run_id = latest
            cards = [
                {"label": "%s/%s %s" % (step, task_id, name), "card": card_id}
                for _, step, task_id, name, card_id in sorted(
                    find_cards(flow, run_id), reverse=True
                )
            ]
            resp = {"status": "ok", "flow": flow, "run_id": run_id, "cards": cards}
        else:
            resp = {"status": "no runs"}
        self._response(resp, is_json=True)

    def get_card(self, suffix):
        flow, run_id, step, task_id, fname = suffix.split("/")
        url = os.path.join(
            metaflow_config.CARD_S3ROOT,
            flow,
            "runs",
            run_id,
            "steps",
            step,
            "tasks",
            task_id,
            "cards",
            fname + ".html",
        )
        with S3() as s3:
            self._response(s3.get(url).blob)

    def get_data(self, suffix):
        flow, run_id, step, task_id, fname = suffix.split("/")
        url = os.path.join(
            metaflow_config.CARD_S3ROOT,
            flow,
            "runs",
            run_id,
            "steps",
            step,
            "tasks",
            task_id,
            "runtime",
            fname + ".data.json",
        )
        with S3() as s3:
            obj = s3.get(url, return_missing=True)
            if obj.exists:
                self._response({'status': 'ok', 'payload': json.loads(obj.blob)}, is_json=True)
            else:
                self._response({'status': 'not found'}, is_json=True)

    def _response(self, body, is_json=False):
        self.send_response(200)
        mime = "application/json" if is_json else "text/html"
        self.send_header("Content-type", mime)
        self.end_headers()
        if is_json:
            self.wfile.write(json.dumps(body).encode("utf-8"))
        else:
            self.wfile.write(body)            

    ROUTES = {"runinfo": get_runinfo, "card": get_card, "data": get_data}


def find_latest_run():
    def _list():
        for flow in os.listdir(".metaflow"):
            path = os.path.join(".metaflow", flow, "latest_run")
            if os.path.exists(path):
                with open(path) as f:
                    yield os.path.getmtime(path), flow, f.read()

    for _, flow, run_id in sorted(_list(), reverse=True):
        return flow, run_id


def task_time(pathspec):
    if pathspec not in TASK_CACHE:
        TASK_CACHE[pathspec] = Task(pathspec).created_at
    return TASK_CACHE[pathspec]


def find_cards(flow, run_id):
    root = os.path.join(metaflow_config.CARD_S3ROOT, flow, "runs", run_id, "")
    with S3() as s3:
        objs = s3.list_recursive([root])
        for obj in objs:
            if obj.key.startswith("steps/") and obj.key.endswith('.html') and obj.size > 0:
                _, step, _, task_id, _, fname = obj.key.split("/")
                name = fname.split("-")[-2]
                pathspec = f"{flow}/{run_id}/{step}/{task_id}"
                card_id = "%s/%s" % (pathspec, fname.split(".")[0])
                yield task_time(pathspec), step, task_id, name, card_id


if __name__ == "__main__":
    namespace(None)
    server_address = ("", 8000)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    httpd.serve_forever()
