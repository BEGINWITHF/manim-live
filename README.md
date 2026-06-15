# Manteraction

a package which intends to achieve live-interaction Manim with enhanced UI interaction system, using Vulkan to enhance Manim render speed, aiming to lower the difficulty of Manim creation.

## key features

No matter ManimGL by Grant Sandrson or ManimCE by Manim Community, it's essense is a package of python, which needs strong coding skill. The essense of coding makes even starting the first HelloWorld scene of manim extremely difficult for people who have never experienced coding. Manteraction's key features aims to lower the difficulty of programming.

### 1. Application Form

Manteraction uses the application form,  packaging Manim, Vulkan, and other packages into one application. It makes the installation of Manim and other extended packages incredibly easy.

### 2. UI-interaction system

Besides installation, the actual coding of Manim is notoriously hard for beginner programmers. Manteraction uses a UI-interaction system to make the creation of Mobjects(e.g., Text, Lines, Graph) intuitive and interactive. Also, manteraction adds a timeline feature to make the building of the scene more intuitive.

### 3. data storing

A Manteraction file is classified into three types: original video-output form, PPT-like form, and website form. When editing, the original video-output form data is automatically stored in a file with the  suffix .mt, and the PPT-like form data in .mtppt, and the website in .mtweb. Directly opening the file will automatically present the result form, while opening this file in Manteraction will enter editing streamline.

### newly added elements

In addition to Manim's interaction elements, Manteraction intends to implement two new elements for better interaction. They can affect other Mobjects‘ appearance.

#### 1. checkbox

A checkbox is a hollow square and can be torn solid when clicking. This feature is applicable for Boolean result adjustments.

#### 2. slider

A slider is a bar having a label on it, in which the label can be dragged. This feature is applicable for multi-valued result adjustments(discrete or continuous).

## Milestones

### 1. manim-vulkan

manim-vulkan is a projects which integrates manim to vulkan, enhancing manim render and output speed.

#### intended feature

##### 1.1 Basic rendering and fitting

- intensely enhancing render speed✅
- basic elements rendering(square, circle, etc)✅

------

#### The following feature is not supported now

------

- both Windows/Mac support
- support window adjustment

##### 1.2 supplementary rendering

- label rendering(arrow tip,etc.)
- transformation and animation rendering
- formula rendering(latex, typst supportive)
- 3d rendering
- have the same code format as the original ManimCE

##### 1.3 integrated render

- multi-3D scene rendering
- camera shifting rendering
- live interaction(checkbox, slider, drag, etc.)
- fit for a later iteration of Manim
- other system( linux etc. support)

### 2. manteraction

Based on manim-vulkan, manteraction is an application with an enhanced UI for manim editing and creating

#### intended features

##### 2.1. basic UI interference

- godot-like interaction logic
- basic UI for lime, square, etc
- store file in .mtppt
- successfully achieve video interaction
- timeline feature(janim)

##### 2.2 integrated features

- mindmap support
- VGroup symbol support
- support interactive adjustments
- plugin support
- support .mt, .mtweb

##### 2.3 Other features

- AI vibe creating support
