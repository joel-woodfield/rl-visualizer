# RL-Visualizer

RL-Visualizer is a simple, easy-to-use software to visualize RL algorithms. It is designed to be easily compatible with many RL frameworks.


## Simple Example Usage
```python
# Evaluation code
import rlviz
rlviz.init_screens(["obs", "latent"], [rlviz.FrameType.COLOR, rlviz.FrameType.LOGGRID])

obs = env.reset()
for k in range(num_steps):
    rlviz.add(obs, "obs")
    latent = encoder(obs)
    rlviz.add(latent, "latent")
    action = q_head(latent)
    rlviz.end_step()

    obs, action, reward, next_obs, done = env.step(action)

rlviz.end_recording("video.mp4")
```

## Real Usage with CleanRL
```python
def evaluate(
    env_id: str,
    eval_episodes: int,
    eval_agent: torch.nn.Module,
    device: torch.device = torch.device("cpu"),
    capture_video: bool = True,
    gamma: float = 0.99,
    video_output_path: str = "video.mp4",
):
    envs = gym.vector.SyncVectorEnv([make_env(env_id, 0, capture_video, "eval", gamma)])
    eval_agent = eval_agent.to(device)
    eval_agent.eval()

    rlviz.init_screens(
        ["obs", "latent"],
        [rlviz.FrameType.COLOR, rlviz.FrameType.LOGGRID],
    )
    rlviz.start_recording()

    obs, _ = envs.reset()
    episodic_returns = []
    while len(episodic_returns) < eval_episodes:
        rlviz.add(torch.Tensor(obs[0, 0]), "obs")
        rlviz.end_step()

        actions = eval_agent.get_action(torch.Tensor(obs).to(device))

        next_obs, _, _, _, infos = envs.step(actions)
        if "final_info" in infos:
            for info in infos["final_info"]:
                if "episode" not in info:
                    continue
                print(
                    f"eval_episode={len(episodic_returns)}, episodic_return={info['episode']['r']}")
                episodic_returns += [info["episode"]["r"]]
        obs = next_obs

    rlviz.end_recording(video_output_path)
    return episodic_returns
```
