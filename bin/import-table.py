#!/usr/bin/env python

import sys
import os.path    
import logging
import json

import mysql.connector

if __name__ == '__main__':

    import optparse
    import ConfigParser

    opt_parser = optparse.OptionParser("""import-table.py -t <TABLE> -c <CONFIG> /path/to/data/file""")

    opt_parser.add_option('-t', '--table', dest='table', action='store', default=None, help='')
    opt_parser.add_option('-c', '--config', dest='config', action='store', default=None, help='')

    opt_parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Be chatty (default is false)')
    options, args = opt_parser.parse_args()

    if options.verbose:	
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not os.path.exists(options.config):
        logging.error("Missing config file")
        sys.exit()

    cfg = ConfigParser.ConfigParser()
    cfg.read(options.config)

    db_cfg = {
        'user': cfg.get('maplibs', 'db_user'),
        'password': cfg.get('maplibs', 'db_pswd'),
        'host': cfg.get('maplibs', 'db_host'),
        'database': cfg.get('maplibs', 'db_name')
    }

    conn = mysql.connector.connect(**db_cfg)
    curs = conn.cursor()

    logging.warning("OMG ESCAPE TABLE NAME %s" % options.table)
    table = options.table

    for path in args:

        path = os.path.abspath(path)

        try:
            fh = open(path, 'r')
            data = json.load(fh)
            data = data.get(options.table, [])
        except Exception, e:
            logging.error("failed to load %s, because %s" % (path, e))
            continue

        for row in data:
            print row

            # temp...
            del(row['label_clean'])

            cols = []
            values = []

            for k, ignore in row.items():

                v = "%" + "(%s)s" % k

                cols.append(k)
                values.append(v)

            cols = ",".join(cols)
            values = ",".join(values)
                            
            sql = "INSERT INTO " + table + " (" + cols + ") VALUES(" + values + ")"
            logging.debug(sql)

            try:
                curs.execute(sql, row)                
                conn.commit()
            except mysql.connector.errors.IntegrityError, e:

                conn.rollback()

                if e.errno == 1062:
                    # update
                    pass
                else:
                    raise Exception, e


            except Exception, e:

                conn.rollback()
                raise Exception, e

