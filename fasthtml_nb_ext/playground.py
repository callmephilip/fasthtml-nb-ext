import time
from typing import Optional, Callable
from fasthtml.common import *
from fasthtml.jupyter import *
from IPython.display import HTML, display
from fasthtml_nb_ext.server import ColabFriendlyJupyUvi

@dataclass
class PlaygroundContext: app: FastHTML; rt: Callable; server: ColabFriendlyJupyUvi; host: str

class Playground:
  ctx: Optional[PlaygroundContext] = None
  app_config: dict = {}

  @staticmethod
  def config(**kw): Playground.app_config = kw

  def __init__(self, path="/"): self.path = path
  def __enter__(self) -> PlaygroundContext:
    if not Playground.ctx:
      app = FastJupy(**Playground.app_config)
      rt, server = app.route, ColabFriendlyJupyUvi(app, port=8000, start=False)
      host = server.start()
      
      if not host: raise Exception("Failed to start server")
      if not host.startswith("http://localhost"): time.sleep(5) # wait for DNS propagation
      
      Playground.ctx = PlaygroundContext(app, rt, server, host)
    return Playground.ctx

  def __exit__(self, type, value, traceback):
    url = f"{Playground.ctx.host}{self.path}"
    iframe_height = "auto"
    display(HTML(f'<iframe src={url} style="width: 100%; height: {iframe_height}; border: none;" ' + """onload="{
        let frame = this;
        window.addEventListener('message', function(e) {
            if (e.data.height) frame.style.height = (e.data.height+1) + 'px';
        }, false);
    }" allow="accelerometer; autoplay; camera; clipboard-read; clipboard-write; display-capture; encrypted-media; fullscreen; gamepad; geolocation; gyroscope; hid; identity-credentials-get; idle-detection; magnetometer; microphone; midi; payment; picture-in-picture; publickey-credentials-get; screen-wake-lock; serial; usb; web-share; xr-spatial-tracking"></iframe> """))
    return True
  