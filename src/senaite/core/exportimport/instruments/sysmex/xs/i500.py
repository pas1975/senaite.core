# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

""" Sysmex XS 500i
"""
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from . import SysmexXSImporter, SysmexXSCSVParser
import json
import traceback

title = "Sysmex XS - 500i"

def getForm(instrument_name, request):
    """
    Since 500i and 1000i print the same results structure (https://jira.bikalabs.com/browse/LIMS-1571), this function
    will be overwrote on i1000 importer to save code.
    :param instrument_name: a string containing the instrument's name with the format: 'sysmex_xs_500i'
    :param request: the request object
    :returns: a dictionary with the requests results.
    """
    d = {'infile': request.form[instrument_name + '_file'],
         'fileformat': request.form[instrument_name + '_format'],
         'artoapply': request.form[instrument_name + '_artoapply'],
         'override': request.form[instrument_name + '_override'],
         'sample': request.form.get(instrument_name + '_sample',
                                    'requestid'),
         'instrument': request.form.get(instrument_name + '_instrument', None)}
    return d

def Import(context, request, instrumentname='sysmex_xs_500i'):
    """ Sysmex XS - 500i analysis results
    """
    # I don't really know how this file works, for this reason I added an 'Analysis Service selector'.
    # If non Analysis Service is selected, each 'data' column will be interpreted as a different Analysis Service. In
    # the case that an Analysis Service was selected, all the data columns would be interpreted as different data from
    # an unique Analysis Service.
    formitems = getForm(instrumentname, request)
    infile = formitems['infile']
    fileformat = formitems['fileformat']
    artoapply = formitems['artoapply']
    override = formitems['override']
    instrument = formitems['instrument']
    errors = []
    logs = []
    warns = []

    # Load the most suitable parser according to file extension/options/etc...
    parser = None
    if not hasattr(infile, 'filename'):
        errors.append(_("No file selected"))
    if fileformat == 'csv':
        # Get the Analysis Service selected, if there is one.
        analysis = request.form.get('analysis_service', None)
        if analysis:
            # Get default result key
            defaultresult = request.form.get('default_result', None)
            # Rise an error if default result is missing.
            parser = SysmexXS500iCSVParser(infile, analysis, defaultresult) if defaultresult \
                     else errors.append(t(_("You should introduce a default result key.",
                                             mapping={"fileformat": fileformat})))
        else:
            parser = SysmexXS500iCSVParser(infile)
    else:
        errors.append(t(_("Unrecognized file format ${fileformat}",
                          mapping={"fileformat": fileformat})))

    if parser:
        # Load the importer
        status = ['sample_received', 'to_be_verified']
        if artoapply == 'received':
            status = ['sample_received']
        elif artoapply == 'received_tobeverified':
            status = ['sample_received', 'to_be_verified']

        over = [False, False]
        if override == 'nooverride':
            over = [False, False]
        elif override == 'override':
            over = [True, False]
        elif override == 'overrideempty':
            over = [True, True]

        importer = SysmexXS500iImporter(parser=parser,
                                        context=context,
                                        allowed_ar_states=status,
                                        allowed_analysis_states=None,
                                        override=over,
                                        instrument_uid=instrument)
        tbex = ''
        try:
            importer.process()
        except Exception:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

    results = {'errors': errors, 'log': logs, 'warns': warns}

    return json.dumps(results)


class SysmexXS500iCSVParser(SysmexXSCSVParser):

    def getAttachmentFileType(self):
        return "Sysmex XS 500i CSV"


class SysmexXS500iImporter(SysmexXSImporter):

    def getKeywordsToBeExcluded(self):
        return []
