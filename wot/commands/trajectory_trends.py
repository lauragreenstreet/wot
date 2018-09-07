#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import wot.io
import wot.ot


def main(argv):
    parser = argparse.ArgumentParser(description='Generate mean expression profiles for ' \
                                                 'ancestors and descendants of each cell set at the given timepoint')
    parser.add_argument('--matrix', help=wot.commands.MATRIX_HELP, required=True)
    parser.add_argument('--tmap', help=wot.commands.TMAP_HELP, required=True)
    parser.add_argument('--cell_set', help=wot.commands.CELL_SET_HELP, required=True)
    parser.add_argument('--time', help='Timepoint to consider', required=True)
    parser.add_argument('--out', help='Prefix for output file names', default='trajectory')

    args = parser.parse_args(argv)
    tmap_model = wot.model.TransportMapModel.from_directory(args.tmap)
    cell_sets = wot.io.read_sets(args.cell_set, as_dict=True)
    populations = tmap_model.population_from_cell_sets(cell_sets, at_time=args.time)

    if len(populations) == 0:
        raise ValueError("No cells from the given cell sets are present at that time")

    trajectory_ds = tmap_model.compute_trajectories(populations)
    matrix = wot.io.read_dataset(args.matrix)
    results = wot.ot.compute_trajectory_trends_from_trajectory(trajectory_ds, matrix)
    # output genes on columns, time on rows, one file per trajectory

    for j in range(len(results)):
        mean, variance = results[j]
        trajectory_name = trajectory_ds.col_meta.index.values[j]
        basename = args.out + '_' + trajectory_name
        wot.io.write_dataset(mean, basename + '.mean')
        wot.io.write_dataset(variance, basename + '.variance')
