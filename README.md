# How to use

```
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
