# file: text.py
# vim:fileencoding=utf-8:ft=python:fdm=marker
# Copyright © 2011-2019 R.F. Smith <rsmith@xs4all.nl>. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Created: 2011-03-27 13:59:17 +0200
# Last modified: 2020-12-26T23:23:02+0100
"""Text output routines for lamprop."""

# import sys
from .version import __version__
import lp.core as core

# Data

_t = [
    "thickness: {0:.2f} mm, density: {1:4.2f} g/cm³",
    "laminate weight: {0:.0f} g/m², resin consumption: {1:.0f} g/m²",
    "ν_xy = {0:7.5f}",
    "ν_yx = {0:7.5f}",
    "α_x = {0:9.4g} K⁻¹, α_y = {1:9.4g} K⁻¹",
    "    [g/m²]   [°]  [%]",
]

# Platforms that don't support UTF-8 get ASCII text.
# enc = sys.stdout.encoding
# if not enc or enc.lower() != 'utf-8':
#     _t = ["thickness: {0:.2f} mm, density: {1:4.2f} g/cm3",
#           "laminate weight: {0:.0f} g/m2, resin consumption: {1:.0f} g/m2",
#           "v_xy = {0:7.5f}",
#           "v_yx = {0:7.5f}",
#           "a_x = {0:9.4g} 1/K, a_y = {1:9.4g} 1/K",
#           "    [g/m2] [deg]  [%]"]


def out(lam, eng, mat):  # {{{1
    """Return the output as a list of lines."""
    lines = [
        "Generated by lamprop {0}".format(__version__),
        "laminate: {0}".format(lam.name),
    ]
    if eng:
        lines += engprop(lam)
    if mat:
        lines += matrices(lam)
        lines += fea(lam)
        lines += tensor(lam)
    lines.append("")
    return lines


def engprop(l):  # {{{1
    """Return the engineering properties as a plain text table in the form of
    a list of lines."""
    s = "fiber volume fraction: {0:.3g}%, fiber weight fraction: {1:.3g}%"
    lines = [
        _t[0].format(l.thickness, l.ρ),
        s.format(l.vf * 100, l.wf * 100),
        _t[1].format(l.fiber_weight + l.resin_weight, l.resin_weight),
        "num weight angle   vf fiber",
        _t[5],
    ]
    s = "{0:3} {1:6g} {2:5g} {3:4.3g} {4}"
    for ln, la in enumerate(l.layers, start=1):
        lines.append(
            s.format(ln, la.fiber_weight, la.angle, la.vf * 100, la.fiber.name)
        )
    lines.append("In-plane engineering properties:")
    lines += [
        f"E_x  = {l.Ex:.0f} MPa, E_y  = {l.Ey:.0f} MPa, E_z  = {l.Ez:.0f} MPa ",
        f"G_xy  = {l.Gxy:.0f} MPa, G_xz  = {l.Gxz:.0f} MPa, G_yz  = {l.Gyz:.0f} MPa ",
        _t[2].format(l.νxy),
        _t[4].format(l.αx, l.αy),
    ]
    return lines


def matrices(l):  # {{{1
    """Return the ABD, abd, H and h matrices as plain text."""
    lines = ["In-plane stiffness (ABD) matrix:"]
    matstr = "|{:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4}|"
    hstr = "|{:< 10.4} {:< 10.4}|"
    for n in range(6):
        m = matstr.format(
            l.ABD[n][0], l.ABD[n][1], l.ABD[n][2], l.ABD[n][3], l.ABD[n][4], l.ABD[n][5]
        )
        lines.append(m)
    lines.append("Transverse (H) stiffness matrix:")
    for n in range(2):
        h = hstr.format(l.H[n][0], l.H[n][1])
        lines.append(h)
    lines.append("In-plane compliance (abd) matrix:")
    for n in range(6):
        m = matstr.format(
            l.abd[n][0], l.abd[n][1], l.abd[n][2], l.abd[n][3], l.abd[n][4], l.abd[n][5]
        )
        lines.append(m)
    lines.append("Transverse (h) compliance matrix:")
    for n in range(2):
        h = hstr.format(l.h[n][0], l.h[n][1])
        lines.append(h)
    return lines


def fea(l):  # {{{1
    """Return the material data for abaqus/calculux."""
    lines = ["** Material data for Abaqus / Calculix (SI units):"]
    D = core.toabaqusi(l.C)
    lines.append(f"*MATERIAL,NAME={l.name}")
    if core.isortho(l.C):
        # Convert to abaqus format and SI units
        lines.append("*ELASTIC,TYPE=ORTHO")
        lines.append(
            f"{D[0][0]:.4g},{D[0][1]:.4g},{D[1][1]:.4g},"
            f"{D[0][2]:.4g},{D[1][2]:.4g},{D[2][2]:.4g},"
            f"{D[3][3]:.4g},{D[4][4]:.4g},"
        )
        lines.append(f"{D[5][5]:.4g},293")
    else:
        lines.append("*ELASTIC,TYPE=ANISO")
        lines.append(
            f"{D[0][0]:.4g},{D[0][1]:.4g},{D[1][1]:.4g},"
            f"{D[0][2]:.4g},{D[1][2]:.4g},{D[2][2]:.4g},"
            f"{D[0][3]:.4g},{D[1][3]:.4g},"
        )
        lines.append(
            f"{D[2][3]:.4g},{D[3][3]:.4g},{D[0][4]:.4g},"
            f"{D[1][4]:.4g},{D[2][4]:.4g},{D[3][4]:.4g},"
            f"{D[4][4]:.4g},{D[0][5]:.4g},"
        )
        lines.append(
            f"{D[1][5]:.4g},{D[2][5]:.4g},{D[3][5]:.4g},"
            f"{D[4][5]:.4g},{D[5][5]:.4g},293"
        )
    lines.append("*DENSITY")
    lines.append(f"{l.ρ*1000:.0f}")
    return lines


def tensor(l):  # {{{1
    lines = ["3D stiffness matrix [C], contracted notation:"]
    lines.append("(indices for stress/strain are in the order 11, 22, 33, 23, 13, 12)")
    matstr = "|{:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4} {:< 10.4}|"
    for row in l.C:
        lines.append(matstr.format(row[0], row[1], row[2], row[3], row[4], row[5]))
    lines.append("3D compliance matrix [S], contracted notation:")
    for row in l.S:
        lines.append(matstr.format(row[0], row[1], row[2], row[3], row[4], row[5]))
    lines.append("Engineering properties derived from 3D stiffness matrix:")
    lines.append(f"E_x = {l.tEx:.0f} MPa, E_y = {l.tEy:.0f} MPa, E_z = {l.tEz:.0f} MPa")
    lines.append(f"G_xy = {l.tGxy:.0f} MPa, G_xz = {l.tGxz:.0f} MPa, G_yz = {l.tGyz:.0f} MPa")
    lines.append(f"ν_xy = {l.tνxy:.3f}, ν_xz = {l.tνxz:.3f}, ν_yz = {l.tνyz:.3f}")
    return lines
