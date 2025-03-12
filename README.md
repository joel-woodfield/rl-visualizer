# RL-Visualizer

RL-Visualizer is a simple, easy-to-use software to visualize RL algorithms. It is designed to be easily compatible with many RL frameworks.

## Installation
```bash
pip install git+https://github.com/joel-woodfield/rl-visualizer.git
```

## API Usage
```python
# Evaluation code
import rlviz
rlviz.init_attributes(
    ["obs", "latent", "action", "value"], 
    [rlviz.COLOR, rlviz.GRID, rlviz.TEXT, rlviz.TEXT],
)

rlviz.start_recording()
obs = env.reset()
for k in range(num_steps):
    rlviz.add("obs", obs)
    latent = encoder(obs)
    rlviz.add("latent", latent)

    values = q_head(latent)
    action = argmax(values)
    value = max(values)
    rlviz.add("action", action)
    rlviz.add("value", value)
    rlviz.end_step()

    obs, action, reward, next_obs, done = env.step(action)

rlviz.end_recording("data.h5")
```

## GUI Usage
Run
```bash
rlviz
```
Then select the desired .h5 file to view.
