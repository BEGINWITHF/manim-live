import sys, time
sys.path.insert(0, 'core')
from manim import *
from vulkan_bind import VulkanRender, Add, Wait, set_anim_opacity, get_anim_opacity
from vulkan_bind import FadeOut as VulkanFadeOut
from vulkan_bind import FadeIn as VulkanFadeIn
from vulkan_bind import TransformMatchingShapes as VulkanTMS
from vulkan_bind import Write as VulkanWrite

v = VulkanRender(1920, 1080)

src = Text("abc", font_size=72)
src.shift(LEFT * 3.5)
tar = Text("xyz", font_size=72)
tar.shift(RIGHT * 3.5)
arrow = Text("\u2192", font_size=48)
arrow.shift(UP * 0.2)

class FakeScene:
    def __init__(self):
        self.mobjects = []
    def remove(self, mob):
        if mob in self.mobjects:
            self.mobjects.remove(mob)
    def add(self, *mobs):
        for m in mobs:
            if m not in self.mobjects:
                self.mobjects.append(m)

scene = FakeScene()
scene.add(src, tar, arrow)

# Show initial
v.dll.ClearShapes()
for m in scene.mobjects:
    v._send(m, 0.0)
v.tick()
time.sleep(0.3)
v.dll.SaveScreenshot(b'C:/Users/begin/Desktop/tms2_initial.png')
print('Initial saved')

# Create TMS
tms = VulkanTMS(src, tar, run_time=2.0)

# Simulate play() handler:
# Remove src/tar from scene
if src in scene.mobjects:
    scene.mobjects.remove(src)
if tar in scene.mobjects:
    scene.mobjects.remove(tar)
src._transforming = True
tar._transforming = True

# Begin (creates sub-anims and adds their objects)
tms.begin(time.time())

# Add sub-anim objects to scene
for sub in tms._anims:
    if hasattr(sub, 'mobject') and sub.mobject is not None:
        if sub.mobject not in scene.mobjects:
            scene.mobjects.append(sub.mobject)
    if hasattr(sub, 'target_mobject') and sub.target_mobject is not None:
        if sub.target_mobject not in scene.mobjects:
            scene.mobjects.append(sub.target_mobject)
    ghost = getattr(sub, '_ghost', None)
    if ghost is not None and ghost not in scene.mobjects:
        scene.mobjects.append(ghost)

start = tms.start_time
captured = set()

while True:
    now = time.time()
    elapsed = now - start
    pct = elapsed / 2.0

    tms.interpolate(now)
    if elapsed >= tms.run_time and not tms.finished:
        tms.finish()

    v.dll.ClearShapes()
    for m in scene.mobjects:
        v._send(m, 0.0)
    v.tick()

    for target in [0.25, 0.5, 0.75, 0.99]:
        if target not in captured and pct >= target:
            fname = f'C:/Users/begin/Desktop/tms2_mid_{int(target*100)}.png'
            v.dll.SaveScreenshot(fname.encode('utf-8'))
            captured.add(target)
            print(f'Saved at {target:.1%}')

    if elapsed > tms.run_time + 0.5:
        # Simulate clean_up_from_scene
        tms.clean_up_from_scene(scene)
        v.dll.ClearShapes()
        for m in scene.mobjects:
            v._send(m, 0.0)
        v.tick()
        v.dll.SaveScreenshot(b'C:/Users/begin/Desktop/tms2_final.png')
        print('Final saved')
        break

    time.sleep(0.005)

print('Done')
