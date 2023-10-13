from manim import *
from manim.scene.scene import Scene

config.background_color = "#2c3340"


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

        # add mobjects and play animation
        self.add(arrow, gradient_circle, circle_labels, angle_display)
        self.play(
            Rotate(arrow, angle=360 * DEGREES, about_point=ORIGIN),
            tracker.animate.set_value(360),
            run_time=5,
        )
        self.wait()
