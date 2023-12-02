# %% [markdown]
# # FlyIn Vscode Decorator
#
# @vscode simplifies converting a Python task into a Visual Studio Code server,
# enabling connection and debugging in remote environments.
# It supports installing various extensions for development assistance,
# including Copilot, Python, or Jupyter.
# FlyIn enhances this by automatically generating scripts for task execution,
# using inputs from previous tasks or resuming with updated code.
# Additionally, FlyIn offers numerous advanced features,
# as detailed in the "Advanced Usage" section.

# %%
from flytekit import task
from flytekitplugins.flyin import vscode, workflow

# %% [markdown]
# ## 1. Adding vscode decorator

# %%
@task
@vscode
def train():
    print("forward")
    print("backward")


@workflow
def wf_train():
    train()


# %% [markdown]
# The @vscode decorator, when applied, converts a task into a Visual Studio Code server during runtime. This process overrides the standard execution of the task's function body, initiating a command to start a Visual Studio Code server in advance.
# ## 2. Connecting to the VSCode Server
# You have two methods for connecting:
# 1. **(Recommended)** Set up ingress on the backend to expose a URL on the Flyte console. Details are to be determined (TBD).

# 2. **Use Port-Forwarding:** Execute the command:
#    ```
#    $ kubectl port-forward <pod name> <port>
#    ```
#    Then, open a browser and navigate to `localhost:port`. You will be presented with the interface as shown in the image below.

# ## 3. Interactively Debugging Task
#
# To run the task in VSCode, select "Run and debug" from the left panel and execute the "interactive debugging" configuration. This will run your task with inputs from the previous task. It's important to note that the task runs entirely within VSCode and does not write the output to Flyte storage.
#
# For inspecting intermediate states, set breakpoints in the Python code and use the debugger for tracing.
#
# The `launch.json` file generated by FlyIn simply offers a convenient method to run the task. You can still use VSCode as you would locally. For instance, you can run a Python script directly from the embedded terminal using `python hello.py`.
#
# # Advanced Usage
# ## 1. Installing Extensions
# Like local VSCode, you can install a variety of extensions to assist development. Available extensions differ from official VSCode for legal reasons and are hosted on [Open VSX Registry](https://open-vsx.org/).
#
# Python and Jupyter extensions are installed by default. Additional extensions can be added as shown below:
#
# %%
from flytekit import task, workflow
from flytekitplugins.flyin import COPILOT_EXTENSION, VscodeConfig, vscode

config = VscodeConfig()
config.add_extensions(COPILOT_EXTENSION)  # Use predefined URL
config.add_extensions(
    "https://open-vsx.org/api/vscodevim/vim/1.27.0/file/vscodevim.vim-1.27.0.vsix"
)  # Copy raw URL from Open VSX


@task(container_image="localhost:30000/flytekit-flyin:0.0.0")
@vscode(config=config)
def t_ext():
    pass


@workflow
def wf_ext():
    t_ext()


# ## 2. Resource Management
# To manage GPU resources, FlyIn can terminate pods after a period of idleness (no active HTTP connections). Idleness is monitored via a heartbeat file.
# %%
from flytekit import task, workflow
from flytekitplugins.flyin import vscode


@task
@vscode(max_idle_seconds=60000)  # 60000 seconds
def task_with_max_idle():
    pass


@workflow
def wf_idle():
    task_with_max_idle()


# ## 3. Pre/Post Execution
#
# For tasks requiring setup or cleanup, FlyIn allows execution of functions before and after VSCode starts.
#
# %%
from flytekit import task, workflow
from flytekitplugins.flyin import vscode


def set_up_proxy():
    print("set up")


def push_code():
    print("push code")


@task
@vscode(pre_execute=set_up_proxy, post_execute=push_code)
def t_hook():
    pass


@workflow
def wf_hook():
    task_with_max_idle()


# ## 4. Running Along with Task
# FlyIn can initiate VSCode after task failure, preventing task termination and enabling inspection.
# %%
from flytekit import task, workflow
from flytekitplugins.flyin import vscode


@task
@vscode(run_task_first=True)
def t_exception():
    return 1 // 0  # causes exception


@workflow
def wf_exception():
    task_with_max_idle()


# ## 5. Prebuilding Image with VSCode
# To skip downloading VSCode and extensions at runtime,
# they can be prebuilt into a Docker image, accelerating setup.
# ```Dockerfile
# Include this line if 'curl' isn't installed in the image.
# RUN apt-get -y install curl
# Download and extract VSCode.
# RUN mkdir -p /tmp/code-server
# RUN curl -kfL -o /tmp/code-server/code-server-4.18.0-linux-amd64.tar.gz https://github.com/coder/code-server/releases/download/v4.18.0/code-server-4.18.0-linux-amd64.tar.gz
# RUN tar -xzf /tmp/code-server/code-server-4.18.0-linux-amd64.tar.gz -C /tmp/code-server/
# ENV PATH="/tmp/code-server/code-server-4.18.0-linux-amd64/bin:${PATH}"
# Download and install extensions
