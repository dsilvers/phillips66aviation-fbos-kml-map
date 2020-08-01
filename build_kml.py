import json
import requests
import simplekml
import time


STATES = ('AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT',
          'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL',
          'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
          'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE',
          'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
          'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD',
          'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
          'WI', 'WY')

PHILLIPS_JSON_URL = 'https://www.phillips66aviation.com/content/psx/psx_av/en/find-fbos-retail-pricing/jcr:content/root/responsivegrid/map.json?MODE=STATE&SEARCH={}&RADIUS=99999&END=END&STATE='

KML_FILENAME = "Phillips66_FBOs.kml"
NOT_ACCEPTING_CC = 0  # just a counter
AIRPORT_COUNT = 0
FBO_COUNT = 0


kml = simplekml.Kml()

for state in STATES:
    request_obj = requests.get(PHILLIPS_JSON_URL.format(state))

    try:
        airport_data = request_obj.json()['search']['airport']
    except json.decoder.JSONDecodeError:
        print("{} - no airports found".format(state))
        continue

    print("{} - {}".format(state, len(airport_data)))

    # Whomever designed this JSON schema is a terrible person.
    try:
        airport_data[0]
    except KeyError:
        airport_data = [airport_data]

    for airport in airport_data:
        AIRPORT_COUNT += 1

        # Again, whomever ever designed this JSON schema is a terrible person.
        fbos = []
        try:
            airport['fbo'][0]
        except KeyError:
            fbos.append(airport['fbo'])
        else:
            for fbo in airport['fbo']:
                fbos.append(fbo)

        for fbo in fbos:
            try:
                # If this is yes (or is set?), they accept phillips credit cards
                if fbo['fuel']['p66cc'] == "Y":
                    FBO_COUNT += 1
                    kml.newpoint(
                        name=airport['id'],
                        description="{} ({}) - {} - {}, {}".format(
                            airport['name'],
                            airport['id'],
                            fbo['fboname'],
                            airport['city'],
                            airport['state'],
                        ),
                        coords=[(
                            # Who the heck puts longitude before latitude? This library, apparently.
                            fbo['longitude'],
                            fbo['latitude'],
                        )],
                    )
                else:
                    NOT_ACCEPTING_CC += 1
            except AttributeError:
                NOT_ACCEPTING_CC += 1

    # Don't be a complete jerk to the Phillips66 website....
    if(state != STATES[-1]):
        time.sleep(1.0)

print("-----\nWriting KML: {}".format(KML_FILENAME))
kml.save(KML_FILENAME)

print("-----\nTotal Airports: {}\nTotal FBOs: {}\nTotal not accepting CCs: {}".format(
    AIRPORT_COUNT,
    FBO_COUNT,
    NOT_ACCEPTING_CC,
))
