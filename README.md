# Manteraction

a package which intends to achieve live-interaction Manim with enhanced UI interaction system, using Vulkan to enhance Manim render speed, aiming to lower the difficulty of Manim creation.

## key features

No matter ManimGL by Grant Sandrson or ManimCE by Manim Community, it's essense is a package of python, which needs strong coding skill. The essense of coding makes even starting the first HelloWorld scene of manim extremely difficult for people who have never experienced coding. Manteraction's key features aims to lower the difficulty of programming.

### 1. application form

Manteraction uses the application form,  packaging Manim, Vulkanl and other packages to one application. It making the installation of manim and other extended packages incredibly easy.

### 2. UI-interaction system

Besides installation, the actual coding of Manim is notoriously hard for beginner programmers. Manteraction uses UI-interaction system to make the creation of Mobjects(e.g. Text, Lines, Graph) intuitive and interactive. Also, manteraction adds a timeline feature to make the build of scene more intuitive.

### 3. data storing

an Manteraction file is classified with three type: original video-output form, PPT-like form, and website form. When editing, the original video-output form data is automatically stored in a file with suffix .mt, and the PPT-like form data in .mtppt, and website in .mtweb. directly open the file will automatically present the result form, while open these file in Manteraction will enter editing streamline.

### newly added elements

In addition of Manim's interaction elements, Manteraction intends to implement two newly elements for better interaction. They can affect other Mobject's appearance.

#### 1. checkbox

Checkbox is a hollow square and can torn solid when clicking. This feature is applicable for boolean result adjustments.

#### 2. slider

Slider is a bar having a label on it, in which the label can be dragged. This feature is applicable for mullti-valued result adjustments(discreate or continuous).

## Milestones

### 1. manim-vulkan

manim-vulkan is a projects which integrates manim to vulkan, enhancing manim render and output speed.

#### intended fearure

##### 1.1 basic rendering and fitting

- intensely enhancing render speed✅
- basic elements rendering(square, circle, etc)✅

------

#### the following feature is not supported now

------

- both windows/mac support
- support window adjustment

##### 1.2 supplementary rendering

- label rendering(arrow tip,etc.)
- transformation and animation rendering
- formula rendering(latex, typst supportive)
- 3d rendering
- have same code format with the original ManimCE

##### 1.3 integrated render

- multi-3d scene rendering
- camera shifting rendering
- live interaction(checkbox, slider, drag, etc.)
- fit for later iteration of Manim
- other system( linux etc. support)

### 2. manteraction

Based on manim-vulkan, manteraction is an application with enhanced UI interface for manim editing and creating

#### intended features

##### 2.1. basic UI interference

- godot-like interaction logic
- basic UI for lime, square, etc
- store file in .mtppt
- succesfully achieve video interaction
- timeline feature(janim)

##### 2.2 integrated features

- mindmap support
- VGroup symbol support
- support interactive adjustments
- plugin support
- support .mt, .mtweb

##### 2.3 other features

- AI vibe creating support

## citation

The Manim Community Developers. (2026). Manim – Mathematical Animation Framework (Version v0.20.1) [Computer software]. <https://www.manim.community/>
