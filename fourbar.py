from manim import *
from manim.scene.scene import Scene

# colors I like:
# origmi white: '#E5E2DA'
# deep_ocean: "#102f48","#0e1a25",#0c1c24
# deep_ocean comp: '#52687f'
# deep_ocean_greys: "#bbc3cc", #808996, '#556578', '#404e60', '#2c3340'
config.background_color = "#0e1a25"

# steel blue: "#70a1d7"
# cornflower blue: "#5ca4cf"
# light coral: "#ff6b6b"
# pastel yellow: "#ffd166", #ffc857
# dark periwinkle: #4d5aaf

# possible bg: "#040414"
# grid bg: "#070b0f"
# grid line and border: "#2a333c",#3b434c


class Constraints(Scene):
    def construct(self):
        # define square, joint and grid
        square = RoundedRectangle(
            fill_color="#5ca4cf",
            fill_opacity=1,
            stroke_width=0,
            height=1.0,
            width=1.0,
            corner_radius=0.1,
        ).scale(0.5)
        joint = Dot(color="#ffc857").move_to([0, 1.5, 0])
        world_origin = Dot(color="#ff6b6b")
        grid = NumberPlane(
            background_line_style={
                "stroke_color": "#2a333c",
                "stroke_width": 2,
                "stroke_opacity": 0.3,
            },
            axis_config={"color": "#2a333c", "stroke_width": 3},
        ).scale(0.5)
        border = SurroundingRectangle(
            grid, corner_radius=0.2, buff=0.04, color="#2a333c"
        )
        grid.add_background_rectangle(color="#070b0f", corner_radius=0.2, buff=0.05)

        # create a group of the grid and grid border
        grid_with_border = VGroup(grid, border)

        self.play(GrowFromCenter(grid_with_border))  # uncomment border on grid
        # self.play(FadeIn(grid))

        # self.add(world_origin)
        self.wait()
        self.play(GrowFromCenter(square))
        self.wait()
        # self.play(Create(joint))
        # self.wait()
        self.play(square.animate.move_to([0, 0.5, 0]))
        self.wait()
        self.play(GrowFromCenter(joint))
        self.wait()

        # rotate square about joint (30 deg and back, small pause
        # in between)

        # arrow1 = Arrow(
        #     square.get_center(),
        #     joint.get_center(),
        #     buff=0.1,
        #     stroke_width=3,
        #     max_tip_length_to_length_ratio=0.1,
        # )
        # arrow2 = Arrow(
        #     world_origin.get_center(),
        #     joint.get_center(),
        #     buff=0.1,
        #     stroke_width=3,
        #     max_tip_length_to_length_ratio=0.1,
        # ).shift(LEFT)
        # self.play(FadeIn(arrow1), FadeIn(arrow2))
        # self.wait()


class FourBarTest(Scene):
    def construct(self):
        # create a four bar linkage

        dot = Dot(fill_color="#52687f", fill_opacity=1, stroke_width=0)
        line = Line(ORIGIN, [1, 0, 0], color="#52687f")

        link = VGroup(*[dot, line])
        link2 = link.copy()
        link2[0].set_style(fill_color="#ff6b6b")
        link2[1].set_color(color="#ff6b6b")

        def update(mobj, dt):
            # rotates the link 90deg/sec
            mobj.rotate(dt * 90 * DEGREES, about_point=mobj[1].get_start())

        def update2(mobj, dt):
            mobj.shift(link[1].get_end() - mobj[1].get_start())

        link.add_updater(update)
        link2.add_updater(update2)

        self.add(link, link2)
        self.update_self(0)
        self.wait(4)
        link.suspend_updating()
        self.wait(1)


class PogFourBar(Scene):
    def construct(self):
        def fourBar(theta2):
            """Computes the angles for link b and c of a four bar linkage"""
            # constants
            length_a = 1
            length_b = 2
            length_c = 3
            length_d = 3

            # # convert theta2 to radians
            # theta2 = np.deg2rad(theta2_deg)

            k1 = length_d / length_a
            k2 = length_d / length_c
            k3 = (length_a**2 - length_b**2 + length_c**2 + length_d**2) / (
                2 * length_a * length_c
            )

            A = np.cos(theta2) - k1 - k2 * np.cos(theta2) + k3
            B = -2 * np.sin(theta2)
            C = k1 - (k2 + 1) * np.cos(theta2) + k3

            pm = np.array([+1, -1])  # plus or minus

            theta41, theta42 = 2 * np.arctan2(
                (-B + pm * np.sqrt(B**2 - 4 * A * C)), 2 * A
            )

            k4 = length_d / length_b
            k5 = (length_c**2 - length_d**2 - length_a**2 - length_b**2) / (
                2 * length_a * length_b
            )

            D = np.cos(theta2) - k1 + k4 * np.cos(theta2) + k5
            E = -2 * np.sin(theta2)
            F = k1 + (k4 - 1) * np.cos(theta2) + k5

            M = np.sqrt(E**2 - 4 * D * F)
            theta31, theta32 = (2 * np.arctan2((-E + i), 2 * D) for i in (M, -M))

            return [theta31, theta41, theta32, theta42]

        theta2 = ValueTracker(0)

        colors = ["#52687f", "#ff6b6b", "#ffd166", "#E5E2DA"]
        lengths = [1, 2, 3, 3]

        # create links
        links = VGroup()
        for leng, col in zip(lengths, colors):
            dot = Dot(fill_color=col, fill_opacity=1, stroke_width=0)
            line = Line(ORIGIN, [leng, 0, 0], color=col)
            links.add(VGroup(dot, line))

        # change dot position of links 3 and 4
        links[2][0].move_to(links[2][1].get_end())
        links[3][0].move_to(links[3][1].get_end())
        # connects link 3 to link 4
        links[2].shift(links[3][1].get_end() - links[2][1].get_start())
        # move base link back
        links[3].set_z_index(-1)
        links[2][1].set_z_index(-1)

        # need to set initial state before to rotate from it
        links.initial_state = links.copy()

        def update(mobj):
            mobj.become(mobj.initial_state)

            # update the lines of all links based on tracker and fourBar
            states = fourBar(theta2.get_value())
            states = states[2:]
            states = [theta2.get_value()] + states + [0]

            # rotate link 1
            mobj[0].rotate(states[0], about_point=mobj[0][1].get_start())

            # rotate link 2
            mobj[1].rotate(states[1], about_point=mobj[1][1].get_start())

            # rotate link 3
            mobj[2].rotate(states[2], about_point=mobj[2][1].get_start())

            # move link 2 to the end of link 1
            mobj[1].shift(links[0][1].get_end() - links[1][1].get_start())

        links.add_updater(update)
        self.add(links)
        self.play(
            theta2.animate.set_value(2 * PI),
            run_time=4,
            rate_func=linear,
        )
        theta2.set_value(0)
        self.play(
            theta2.animate.set_value(2 * PI),
            run_time=4,
            rate_func=linear,
        )
        self.wait(2)


class TestLineAngle(Scene):
    def construct(self):
        RADIUS = 0.15
        LINE_LEN = 1
        line = Line(ORIGIN, [LINE_LEN, 0, 0])
        dot = Dot(fill_color=WHITE, fill_opacity=1, stroke_width=0)
        arc = Arc(
            arc_center=[LINE_LEN + RADIUS, 0, 0],
            angle=PI,
            start_angle=PI / 2,
            radius=RADIUS,
        )

        def arc_to_end(arc: Arc):
            return arc.move_to(line.get_end())

        # arc.add_updater(arc_to_end)

        link = VGroup(dot, line, arc)
        t = ValueTracker(0)

        # need to set initial state before to rotate from it
        link.initial_state = link.copy()

        def update(mobj):
            mobj.become(mobj.initial_state)
            mobj.rotate(t.get_value(), about_point=mobj[1].get_start())
            # mobj.set_angle(t.get_value(), about_point=line.get_start())

        link.add_updater(update)
        # arc.add_updater(update)
        self.add(link)
        # link.add_updater(update)
        # self.add(link)

        self.play(
            t.animate.set_value(PI / 2),
            run_time=2,
            rate_func=linear,
        )
        self.wait()


class FourBarTest2(Scene):
    def construct(self):
        def fourBar(theta2):
            """Computes the angles for link b and c of a four bar linkage"""
            # constants
            length_a = 1
            length_b = 2
            length_c = 3
            length_d = 3

            # # convert theta2 to radians
            # theta2 = np.deg2rad(theta2_deg)

            k1 = length_d / length_a
            k2 = length_d / length_c
            k3 = (length_a**2 - length_b**2 + length_c**2 + length_d**2) / (
                2 * length_a * length_c
            )

            A = np.cos(theta2) - k1 - k2 * np.cos(theta2) + k3
            B = -2 * np.sin(theta2)
            C = k1 - (k2 + 1) * np.cos(theta2) + k3

            pm = np.array([+1, -1])  # plus or minus

            theta41, theta42 = 2 * np.arctan2(
                (-B + pm * np.sqrt(B**2 - 4 * A * C)), 2 * A
            )

            k4 = length_d / length_b
            k5 = (length_c**2 - length_d**2 - length_a**2 - length_b**2) / (
                2 * length_a * length_b
            )

            D = np.cos(theta2) - k1 + k4 * np.cos(theta2) + k5
            E = -2 * np.sin(theta2)
            F = k1 + (k4 - 1) * np.cos(theta2) + k5

            M = np.sqrt(E**2 - 4 * D * F)
            theta31, theta32 = (2 * np.arctan2((-E + i), 2 * D) for i in (M, -M))

            return [theta31, theta41, theta32, theta42]

        # create a four bar linkage
        dot = Dot(fill_color="#52687f", fill_opacity=1, stroke_width=0)
        line = Line(ORIGIN, [1, 0, 0], color="#52687f")

        link = VGroup(dot, line)

        links = VGroup(*[link.copy() for j in range(4)])
        colors = ["#52687f", "#ff6b6b", "#ffd166", "#E5E2DA"]
        lengths = [1, 2, 3, 3]
        for index, color in enumerate(colors):
            links[index][0].set_style(fill_color=color)
            links[index].set_color(color=color)
            links[index][1].put_start_and_end_on(ORIGIN, [lengths[index], 0, 0])
            if index >= 2:
                links[index][0].move_to(links[index][1].get_end())

        def update(mobj, dt):
            # "angle of link 1" will start at 10deg and increase 10deg/sec
            angle_1_rad = dt * 10 * DEGREES

            states = fourBar(angle_1_rad)
            # angle_1_rad += 1 * DEGREES
            mobj[0].rotate(angle_1_rad, about_point=mobj[0][1].get_start())
            # moves link 2 to the end of link 1
            mobj[1].shift(mobj[0][1].get_end() - mobj[1][1].get_start())
            # connects link 3 to link 4
            mobj[2].shift(mobj[3][1].get_end() - mobj[2][1].get_start())

            # set x index of link 1 above link 4
            mobj[0].set_z_index(1)
            mobj[1].set_z_index(2)

            # rotate link 2 (theta3)
            mobj[1].rotate(states[2], about_point=mobj[1][1].get_start())

            # rotate link 3 (theta4)

        # def update(mobj, dt):
        #     # rotates the link 90deg/sec
        #     mobj.rotate(dt * 90 * DEGREES, about_point=mobj[1].get_start())

        # def update2(mobj, dt):
        #     mobj.shift(link[1].get_end() - mobj[1].get_start())

        links.add_updater(update)
        # self.update_self(0)
        # link2.add_updater(update2)

        self.add(links)
        # self.update_self(0)
        self.wait(9)
        links.suspend_updating()
        self.wait(1)


class Test(Scene):
    def construct(self):
        line = Line(ORIGIN, RIGHT * 2)
        line.rotate(10 * DEGREES, about_point=ORIGIN)

        self.add(line)
        self.wait(2)


class NewTest(Scene):
    def construct(self):
        # no tracker just a loop
        def fourBar(theta2):
            """Computes the angles for link b and c of a four bar linkage"""
            # constants
            length_a = 1
            length_b = 2
            length_c = 3
            length_d = 3

            # # convert theta2 to radians
            # theta2 = np.deg2rad(theta2_deg)

            k1 = length_d / length_a
            k2 = length_d / length_c
            k3 = (length_a**2 - length_b**2 + length_c**2 + length_d**2) / (
                2 * length_a * length_c
            )

            A = np.cos(theta2) - k1 - k2 * np.cos(theta2) + k3
            B = -2 * np.sin(theta2)
            C = k1 - (k2 + 1) * np.cos(theta2) + k3

            pm = np.array([+1, -1])  # plus or minus

            theta41, theta42 = 2 * np.arctan2(
                (-B + pm * np.sqrt(B**2 - 4 * A * C)), 2 * A
            )

            k4 = length_d / length_b
            k5 = (length_c**2 - length_d**2 - length_a**2 - length_b**2) / (
                2 * length_a * length_b
            )

            D = np.cos(theta2) - k1 + k4 * np.cos(theta2) + k5
            E = -2 * np.sin(theta2)
            F = k1 + (k4 - 1) * np.cos(theta2) + k5

            M = np.sqrt(E**2 - 4 * D * F)
            theta31, theta32 = (2 * np.arctan2((-E + i), 2 * D) for i in (M, -M))

            return [theta31, theta41, theta32, theta42]

        RADIUS = 0.2
        LINE_LEN = 1
        line = Line(ORIGIN, [LINE_LEN, 0, 0])
        dot = Dot(fill_color=WHITE, fill_opacity=1, stroke_width=0)
        arc = Arc(
            arc_center=[LINE_LEN + RADIUS, 0, 0],
            angle=PI,
            start_angle=PI / 2,
            radius=RADIUS,
        )
        link = VGroup(dot, line, arc)
        self.add(link)

        run_time = 1
        theta2 = np.arange(90, 150, run_time)
        for t2 in theta2:
            # 50deg/sec
            self.play(
                Rotate(link, angle=5 * DEGREES, rate_func=linear, about_point=ORIGIN),
                run_time=run_time / 10,
            )

        self.wait()


class SpirographCranks(Scene):
    def construct(self):
        RADIUS = 0.4
        dot = Dot(ORIGIN)
        line = Line(ORIGIN, RIGHT * (2 - RADIUS))
        arc = Arc(arc_center=RIGHT * 2, angle=PI, start_angle=PI / 2, radius=RADIUS)

        crank = VGroup(*[dot, line, arc])

        self.add(crank)

        crank2 = crank.copy()
        crank2.shift([0, 2, 0])

        def update(mobj, dt):
            # this is basically the vector from origin to the 1st crank end
            mobj.shift(crank[2].get_arc_center() - mobj[1].get_start())

            # rotates about the the joint that the two cranks meet
            mobj.rotate(dt * PI, about_point=mobj[1].get_start())

        crank2.add_updater(update)
        self.add(crank2)

        self.play(
            Rotate(crank, angle=2 * PI, rate_func=linear, about_point=ORIGIN),
            run_time=4,
        )

        self.wait()


class MyAxes(Scene):
    def construct(self):
        # ax = Axes(axis_config={"color": RED})
        # self.add(ax)
        c = Circle()
        c.set_style(fill_color="#52687f", fill_opacity=1, stroke_width=0)
        self.play(GrowFromCenter(c))
        self.wait(1)
        self.play(c.animate.scale(1.1), run_time=0.5)
        self.play(c.animate.scale(0), run_time=1)
        self.wait(1)


class GridWithColoredBackground(Scene):
    def construct(self):
        # Create a colored background
        background = Rectangle(
            width=2.0,
            height=2.0,
            fill_color=BLACK,  # You can choose any color you like
            fill_opacity=1,
            stroke_width=0,
        )

        # Create a grid or number plane
        grid = NumberPlane()

        grid.add_background_rectangle(color=BLACK)

        # Set the grid to take up 1/3 of the screen
        grid.scale(1 / 3)

        # Create a border around the grid
        border = SurroundingRectangle(grid, buff=0.1, color=WHITE)

        # Add the background, grid, and border to the scene
        self.add(grid, border)

        # Play the animation
        self.wait(2)


class VGroupExample(Scene):
    def construct(self):
        s1 = Square(color=RED)
        s2 = Square(color=GREEN)
        s3 = Square(color=BLUE)

        s1.next_to(s2, LEFT)
        s3.next_to(s2, RIGHT)

        self.play(Write(s1), Write(s2), Write(s3))

        group = VGroup(s1, s2, s3)

        # scale the entire group
        self.play(group.animate.scale(1.5).shift(UP))

        # only work with one of the group's objects
        self.play(group[1].animate.shift(DOWN * 2))

        # change color and fill
        self.play(group.animate.scale(0.8))
        self.play(group.animate.shift(UP))
