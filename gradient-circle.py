## TUTORIAL 2 MANIM

from manim import *
from manim.scene.scene import Scene

# colors I like:
# origmi white: '#E5E2DA'
# deep_ocean: "#0e1a25",#0c1c24
# deep_ocean comp: '#52687f'
# deep_ocean_greys: "#bbc3cc", #808996, '#556578', '#404e60', '#2c3340'
config.background_color = "#2c3340"

# animations
# mobject - every animation is tied to a mobject
# run_time - the animation's play duration
# rate_func - a function r:[0,1] -> [0,1] controlling animation progression

from colour import Color


class Basic(Scene):
    def construct(self):
        polys = VGroup(
            *[
                RegularPolygon(
                    5,
                    radius=1,
                    fill_opacity=0.5,
                    color=Color(hue=j / 5, saturation=1, luminance=0.5),
                )
                for j in range(5)
            ]
        ).arrange(RIGHT)
        self.play(DrawBorderThenFill(polys), run_time=2)
        self.play(
            Rotate(polys[0], PI, rate_func=lambda t: t),  # rate_func = linear
            Rotate(polys[1], PI, rate_func=smooth),  # rate_func = smooth (default)
            Rotate(polys[2], PI, rate_func=lambda t: np.sin(t * PI)),
            Rotate(polys[3], PI, rate_func=there_and_back),
            Rotate(polys[4], PI, rate_func=lambda t: 1 - abs(1 - 2 * t)),
            run_time=2,
        )
        self.wait(1)


# multiple animations can be passed as positional arguments
# overlapping animations:
# useful for grouping anims: AnimationGroup
# karg: lag_ratio b/w 0 and 1, 0 for simultaneous
# anims_with_timings


class LaggingGroup(Scene):
    def construct(self):
        squares = (
            VGroup(
                *[
                    Square(
                        color=Color(hue=j / 20, saturation=1, luminance=0.5),
                        fill_opacity=0.5,
                    )
                    for j in range(20)
                ]
            )
            .arrange_in_grid(4, 5)
            .scale(0.75)
        )
        self.play(AnimationGroup(*[FadeIn(s) for s in squares], lag_ratio=0.15))


# animation with .animate
# problem: can't pass mobject to play
# solution: use .animate on Mobjects


class Ani1(Scene):
    def construct(self):
        s = Square()
        self.play(s.animate.shift(RIGHT))  # animation of shift by RIGHT
        self.play(s.animate(run_time=2).scale(3))  # pass in keywords
        self.play(s.animate.scale(1 / 2).shift(2 * LEFT))  # chaining


# Note: .animate is NOT aware of how mobjects change, only start and end
# it interpoltes between the start and end


class Ani2(Scene):
    def construct(self):
        s = Square(color=GREEN, fill_opacity=0.5)
        c = Circle(color=RED, fill_opacity=0.5)
        self.add(s, c)

        self.play(s.animate.shift(UP), c.animate.shift(DOWN))
        self.play(VGroup(c, s).animate.arrange(RIGHT, buff=1))
        self.wait(1)
        self.play(c.animate(rate_func=linear).shift(1.5 * LEFT).scale(2))


# other animations: MoveToTarget and Restore

# general framework of these functions:
# 1) create a copy of mobj
# 2) modify it
# 3) transform b/w original and modified


class Ani3(Scene):
    def construct(self):
        c = Circle()
        c.set_style(fill_color=DARK_BLUE, fill_opacity=1, stroke_width=0)

        # MoveToTarget example
        c.generate_target()
        c.target.set_style(fill_color=DARK_GRAY, fill_opacity=1, stroke_width=0)
        c.target.shift(2 * RIGHT + UP).scale(0.5)

        self.add(c)
        self.wait(1)
        self.play(MoveToTarget(c))
        self.wait(1)

        # Restore example
        s = Square(color=DARK_GRAY)
        s.save_state()
        self.play(FadeIn(s))
        self.play(s.animate.set_color(PURPLE).set_opacity(0.5).shift(2 * LEFT).scale(3))
        self.play(s.animate.shift(5 * DOWN).rotate(PI / 3))
        self.wait()
        self.play(Restore(s), run_time=2)


class Practice1(Scene):
    def construct(self):
        c = Circle(color="#0e1a25", radius=2)
        a = Arc(start_angle=0, angle=-90 * DEGREES, color="#0e1a25", radius=2)
        s_start = c.point_at_angle(0)
        s_end1 = c.point_at_angle(PI / 2)

        s1 = Square(side_length=0.3).move_to(s_start)
        s2 = Square(side_length=0.3).move_to(s_start)
        s1.generate_target()
        # s2.generate_target()
        s1.target.move_to(s_end1)
        # s2.target.move_to(s_end2)

        self.add(c, s1, s2, a)
        self.wait(1)
        self.play(MoveToTarget(s1), MoveAlongPath(s2, a), run_time=3)
        self.wait(1)


# Custom Animations via Function
# abstraction: an animation is a function mapping (mobject, completion ratio)
# to a mobject
# tip: store init state in custom mobject attribute


class SimpleCustomAnimation(Scene):
    def construct(self):
        def spiral_out(mobject, t):
            radius = 4 * t
            angle = 2 * t * 2 * PI
            mobject.move_to(radius * np.cos(angle) * RIGHT + np.sin(angle) * UP)
            mobject.set_color(Color(hue=t, saturation=1, luminance=0.5))
            mobject.set_opacity(1 - t)

        d = Dot(color=BLACK)
        self.add(d)
        self.play(UpdateFromAlphaFunc(d, spiral_out, run_time=3))


# Implementing your own Animation class
# - inherit from Animation
# override interpolate_mobject or interpolate_subobject


class Disperse(Animation):
    def __init__(self, mobject, dot_radius=0.05, dot_number=100, **kwargs):
        super().__init__(mobject, **kwargs)
        self.dot_radius = dot_radius
        self.dot_number = dot_number

    # overriding begin method
    def begin(self):
        dots = VGroup(
            *[
                Dot(radius=self.dot_radius).move_to(
                    self.mobject.point_from_proportion(p)
                )
                for p in np.linspace(0, 1, self.dot_number)
            ]
        )
        for dot in dots:
            dot.initial_position = dot.get_center()

            # vector from mobj to dot then scaled by 2
            dot.shift_vector = 2 * (dot.get_center() - self.mobject.get_center())

        dots.set_opacity(0)

        # set the group as the child of the mobject
        self.mobject.add(dots)
        self.dots = dots  # to get dots w/o reference to the parent mobject

        super().begin()

    # overriding clean_up_from_scene
    def clean_up_from_scene(self, scene: "Scene") -> None:
        super().clean_up_from_scene(scene)
        scene.remove(self.dots)

    # override interpolate method
    def interpolate_mobject(self, alpha):
        # need to apply the rate_func
        alpha = self.rate_func(alpha)

        # fade out original mobject and fade in dots in the first half the animation
        if alpha <= 0.5:
            # "family= False" sets the opacity only to the mobj NOT submobjs
            self.mobject.set_opacity(
                1 - 2 * alpha, family=False
            )  # at half of the animation: opacity is 0
            self.dots.set_opacity(2 * alpha)  # at half of the animation: opacity is 1
        else:
            self.mobject.set_opacity(0)  # makes sure mobj is not visible
            self.dots.set_opacity(2 * (1 - alpha))  # fades out dots
            for dot in self.dots:
                # is zero when alpha is 0.5 and the full shift_vector when alpha is 1
                dot.move_to(dot.initial_position + 2 * (alpha - 0.5) * dot.shift_vector)


class CustomAnimationExample(Scene):
    def construct(self):
        st = Star(color=YELLOW, fill_opacity=1).scale(3)
        self.add(st)
        self.wait()
        self.play(Disperse(st, dot_number=200, run_time=4))


class ex1(Scene):
    def construct(self):
        # set positions
        c1 = Dot(color=ORANGE, radius=0.5)
        c2 = Dot(color=BLUE, radius=0.5)
        c3 = Dot(color=DARK_GRAY, radius=0.5)
        c2.next_to(c1, LEFT, buff=0)
        c3.to_edge(DR)
        self.add(c1, c2, c3)

        # get positions
        c3_pos = c3.get_center()
        l1 = Line(ORIGIN, c3_pos)
        self.add(l1)


class ex2(Scene):
    def construct(self):
        # add_updater and animate example
        dot = Dot(color=DARK_GREY, radius=0.5).to_edge(LEFT)
        dec = DecimalNumber().to_edge(UP)

        dec.add_updater(lambda d: d.set_value(dot.get_x()))

        self.add(dot, dec)
        self.play(dot.animate(rate_func=linear).to_edge(RIGHT), run_time=4)
        self.wait(1)


class ex3(Scene):
    def construct(self):
        dot1 = Dot(color=DARK_GREY, radius=0.5)
        dot2 = Dot(color=BLUE, radius=0.3, fill_opacity=0.7)
        dot3 = Dot(color=ORANGE, radius=0.15, fill_opacity=0.7)
        # star = Star(stroke_width=5, color="#52687f")
        sq = Square(stroke_width=5, color="#52687f")

        posd2 = sq.get_corner(UL)
        posd3 = sq.get_left()
        self.add(dot1, dot2.move_to(posd2), dot3.move_to(posd3), sq)


class ex4(Scene):
    def construct(self):
        s = Square(color=BLUE, fill_opacity=0.7)
        s.apply_matrix(
            [
                [1, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
        )  # shear matrix
        self.add(s)


class ex5(Scene):
    def construct(self):
        t1 = Square(color=BLUE, fill_opacity=0.7).move_to([3, 0, 0]).scale(0.5)
        t2 = Triangle(color=BLUE, fill_opacity=0.7).move_to([3, 0, 0]).scale(0.5)
        angle = PI / 3
        dot = Dot(color=DARK_GREY, radius=0.2)
        self.add(t1, t2, dot)

        self.play(
            t1.animate.rotate_about_origin(angle * 2),
            t2.animate.rotate(angle=angle),
            run_time=2,
        )
        self.wait()


class RotateSquareAroundDot(Scene):
    def construct(self):
        # Create a dot at the center of the screen
        dot = Dot(color=DARKER_GRAY)

        # Create a square 3 units to the right
        square1 = Square(side_length=1, color=RED)
        square1.move_to(RIGHT * 3)

        # Create another a square 3 units to the right
        square2 = Square(side_length=1, color=BLUE)
        square2.move_to(RIGHT * 3)

        self.add(dot, square1, square2)

        # Rotate the squares about the dot's origin by 90 degrees (PI/2)
        # square1 using Rotate and square2 using .animate.rotate
        self.play(
            Rotate(square1, angle=PI / 2, about_point=dot.get_center()),
            square2.animate.rotate(angle=PI / 2, about_point=dot.get_center()),
            run_time=3,
        )

        # Wait for a moment before ending the scene
        self.wait(2)


class Gradient(Scene):
    def construct(self):
        t = Text("Hello", gradient=(RED, BLUE), font_size=96)
        self.add(t)


class GradientSine(Scene):
    def construct(self):
        ax = Axes(x_range=(-1, 7), y_range=(-3, 3))
        t = np.arange(0, 2 * PI, 0.1)
        my_colors = color_gradient([DARK_BLUE, ORANGE], len(t))

        def generate_sine_wave_points(time):
            x = time
            y = 2 * np.sin(time * 2)

            return np.column_stack((x, y))

        # alternative
        # plt = ax.plot_parametric_curve(
        #     lambda t: [t,np.sin(2*t),0],
        #     t_range=[0, 5, 1]
        # ).set_stroke_color([DARK_BLUE, PURPLE_E, MAROON_B, ORANGE, YELLOW_C])

        my_func = generate_sine_wave_points(t)

        plt = VGroup(
            *[
                Line(
                    ax.c2p(my_func[i][0], my_func[i][1]),
                    ax.c2p(my_func[i + 1][0], my_func[i + 1][1]),
                ).set_stroke(color=my_colors[i])
                for i in range(len(t) - 1)
            ]
        )

        self.play(Create(plt), run_time=2)
        self.wait(2)


class Arcs(Scene):
    def construct(self):
        # define sector with gradient
        t = np.arange(0, 360, 1)
        my_colors = color_gradient(
            [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, RED], len(t)
        )
        a = VGroup(
            *[
                AnnularSector(
                    start_angle=i * DEGREES,
                    angle=1 * DEGREES,
                    color=my_colors[i],
                    inner_radius=2,
                    outer_radius=2.25,
                ).scale(2)
                for i in range(360)
            ]
        )

        # define arrow
        end_pos = a[0].get_center() - np.array([0.25, 0.0, 0.0])
        arrow = Arrow(start=ORIGIN, end=end_pos, buff=0)

        # a_half = a[:180]

        self.add(a, arrow)


class RotateAndColor(Rotate):
    def __init__(
        self,
        mobject: Mobject,
        angle: float,
        new_color,
        **kwargs,
    ) -> None:
        self.new_color = new_color
        super().__init__(mobject, angle=angle, **kwargs)

    def create_target(self) -> Mobject:
        target = self.mobject.copy()
        target.set_fill(self.new_color)
        target.rotate(
            self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
        return target


# -----
class WeirdRotate4(Scene):
    def construct(self):
        square = Square().set_fill(WHITE, opacity=1.0)

        self.add(square)
        self.wait(1)
        # animate the change of position and the rotation at the same time
        # self.play(Rotate(square,PI))
        self.play(RotateAndColor(square, PI / 8, BLUE, about_point=([-1, 1, 0])))

        self.play(FadeOut(square))
        self.wait(1)


# my example using and update function
# and always_redraw, this defines the mobject and
# gives it an updater with the same code
class GradientCircle(Scene):
    def construct(self):
        # setup tracker and colors for gradient circle
        tracker = ValueTracker(0)
        color_gradient_res = 361
        my_colors = color_gradient(
            [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, RED], color_gradient_res
        )

        def update_color(obj):
            color = tracker.get_value()
            obj.set_color(color=my_colors[int(color)])

        # make a gradient circle made of sectors
        gradient_circle = VGroup(
            *[
                AnnularSector(
                    start_angle=i * DEGREES,
                    angle=1 * DEGREES,
                    color=my_colors[i],
                    inner_radius=2,
                    outer_radius=2.25,
                ).scale(2)
                for i in range(color_gradient_res)
            ]
        )

        # create a circle with a opacity of 0 to use as the positioning of the labels
        circle_ref = Circle(radius=3).set_opacity(0)

        # add labels
        circle_labels = VGroup(
            *[
                Tex(f"{str(i)}$^\circ$").move_to(
                    circle_ref.point_from_proportion(i / 360)
                )
                for i in range(0, 360, 45)
            ]
        )

        # define arrow with updater of update_color
        end_pos = gradient_circle[0].get_center() - np.array([0.25, 0.0, 0.0])
        arrow = Arrow(start=ORIGIN, end=end_pos, buff=0)
        arrow.add_updater(update_color)

        # setup angle display
        angle_display = always_redraw(
            lambda: Tex(f"Angle: {tracker.get_value():.0f} ", font_size=32).to_edge(
                RIGHT + UP, buff=1
            )
        )
        # text.to_edge(RIGHT + UP, buff=1)
        # angle_display = VGroup(integer, text).to_edge(RIGHT + UP, buff=1)
        # integer.add_updater(lambda m: m.set_value(tracker.get_value()))

        # add mobjects and play animation
        self.add(arrow, gradient_circle, circle_labels, angle_display)
        self.play(
            Rotate(arrow, angle=360 * DEGREES, about_point=ORIGIN),
            tracker.animate.set_value(360),
            run_time=5,
        )
        self.wait()
