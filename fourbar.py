from manim import *
from manim.scene.scene import Scene

config.background_color = "#0e1a25"


class FourBar(Scene):
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
        links[3][1].set_z_index(-1)
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
