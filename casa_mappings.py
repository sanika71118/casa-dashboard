# ─────────────────────────────────────────────────────────────────────────────
# CASA Georgia mappings — generated from "2026 Year End CAPTA PIP Report.xlsx"
# (Sheet1: Affiliate Name / Counties).  159 counties, 47 affiliates, no gaps.
# County centroids + FIPS derived from the Census county boundary file.
# ─────────────────────────────────────────────────────────────────────────────

COUNTY_TO_AFF = {
    # Advo-Kids (4)
    'Fayette':'Advo-Kids', 'Pike':'Advo-Kids', 'Spalding':'Advo-Kids', 'Upson':'Advo-Kids',
    # Alapaha (5)
    'Atkinson':'Alapaha', 'Berrien':'Alapaha', 'Clinch':'Alapaha', 'Cook':'Alapaha',
    'Lanier':'Alapaha',
    # Alcovy (2)
    'Newton':'Alcovy', 'Walton':'Alcovy',
    # Appalachian (3)
    'Fannin':'Appalachian', 'Gilmer':'Appalachian', 'Pickens':'Appalachian',
    # Athens-Oconee (2)
    'Clarke':'Athens-Oconee', 'Oconee':'Athens-Oconee',
    # Atlanta (1)
    'Fulton':'Atlanta',
    # Atlantic Area (6)
    'Bryan':'Atlantic Area', 'Evans':'Atlantic Area', 'Liberty':'Atlantic Area',
    'Long':'Atlantic Area', 'McIntosh':'Atlantic Area', 'Tattnall':'Atlantic Area',
    # Augusta (9)
    'Burke':'Augusta', 'Columbia':'Augusta', 'Glascock':'Augusta', 'Lincoln':'Augusta',
    'McDuffie':'Augusta', 'Richmond':'Augusta', 'Taliaferro':'Augusta', 'Warren':'Augusta',
    'Wilkes':'Augusta',
    # CASA Kids (3)
    'Brooks':'CASA Kids', 'Colquitt':'CASA Kids', 'Thomas':'CASA Kids',
    # Carroll (1)
    'Carroll':'Carroll',
    # Central Georgia (3)
    'Bibb':'Central Georgia', 'Crawford':'Central Georgia', 'Peach':'Central Georgia',
    # Chattahoochee (6)
    'Chattahoochee':'Chattahoochee', 'Harris':'Chattahoochee', 'Marion':'Chattahoochee',
    'Muscogee':'Chattahoochee', 'Talbot':'Chattahoochee', 'Taylor':'Chattahoochee',
    # Cherokee CASA (1)
    'Cherokee':'Cherokee CASA',
    # Children's Voice (1)
    'Douglas':"Children's Voice",
    # Clayton (1)
    'Clayton':'Clayton',
    # Coastal Plain (4)
    'Irwin':'Coastal Plain', 'Tift':'Coastal Plain', 'Turner':'Coastal Plain',
    'Worth':'Coastal Plain',
    # Cobb (1)
    'Cobb':'Cobb',
    # Coweta (3)
    'Coweta':'Coweta', 'Heard':'Coweta', 'Meriwether':'Coweta',
    # DeKalb (1)
    'DeKalb':'DeKalb',
    # Dougherty (1)
    'Dougherty':'Dougherty',
    # Enotah (4)
    'Lumpkin':'Enotah', 'Towns':'Enotah', 'Union':'Enotah', 'White':'Enotah',
    # Floyd (1)
    'Floyd':'Floyd',
    # Forsyth (1)
    'Forsyth':'Forsyth',
    # Glynn (5)
    'Appling':'Glynn', 'Camden':'Glynn', 'Glynn':'Glynn', 'Jeff Davis':'Glynn', 'Wayne':'Glynn',
    # Gwinnett (1)
    'Gwinnett':'Gwinnett',
    # Hall-Dawson (2)
    'Dawson':'Hall-Dawson', 'Hall':'Hall-Dawson',
    # Henry (1)
    'Henry':'Henry',
    # Houston (1)
    'Houston':'Houston',
    # Lookout Mt. (4)
    'Catoosa':'Lookout Mt.', 'Chattooga':'Lookout Mt.', 'Dade':'Lookout Mt.',
    'Walker':'Lookout Mt.',
    # Lowndes & Echols (2)
    'Echols':'Lowndes & Echols', 'Lowndes':'Lowndes & Echols',
    # Murray/Whitfield (2)
    'Murray':'Murray/Whitfield', 'Whitfield':'Murray/Whitfield',
    # Northeast Georgia (4)
    'Banks':'Northeast Georgia', 'Habersham':'Northeast Georgia', 'Rabun':'Northeast Georgia',
    'Stephens':'Northeast Georgia',
    # Northern (5)
    'Elbert':'Northern', 'Franklin':'Northern', 'Hart':'Northern', 'Madison':'Northern',
    'Oglethorpe':'Northern',
    # Northwest Ga (2)
    'Bartow':'Northwest Ga', 'Gordon':'Northwest Ga',
    # Ocmulgee (8)
    'Baldwin':'Ocmulgee', 'Greene':'Ocmulgee', 'Hancock':'Ocmulgee', 'Jasper':'Ocmulgee',
    'Jones':'Ocmulgee', 'Morgan':'Ocmulgee', 'Putnam':'Ocmulgee', 'Wilkinson':'Ocmulgee',
    # Ogeechee (4)
    'Bulloch':'Ogeechee', 'Effingham':'Ogeechee', 'Jenkins':'Ogeechee', 'Screven':'Ogeechee',
    # Paulding (1)
    'Paulding':'Paulding',
    # Piedmont (2)
    'Barrow':'Piedmont', 'Jackson':'Piedmont',
    # Polk/Haralson (2)
    'Haralson':'Polk/Haralson', 'Polk':'Polk/Haralson',
    # Rockdale (1)
    'Rockdale':'Rockdale',
    # SOWEGA (17)
    'Ben Hill':'SOWEGA', 'Clay':'SOWEGA', 'Crisp':'SOWEGA', 'Dooly':'SOWEGA', 'Early':'SOWEGA',
    'Lee':'SOWEGA', 'Macon':'SOWEGA', 'Miller':'SOWEGA', 'Quitman':'SOWEGA',
    'Randolph':'SOWEGA', 'Schley':'SOWEGA', 'Seminole':'SOWEGA', 'Stewart':'SOWEGA',
    'Sumter':'SOWEGA', 'Terrell':'SOWEGA', 'Webster':'SOWEGA', 'Wilcox':'SOWEGA',
    # Savannah-Chatham (1)
    'Chatham':'Savannah-Chatham',
    # Southeast Georgia (6)
    'Bacon':'Southeast Georgia', 'Brantley':'Southeast Georgia', 'Charlton':'Southeast Georgia',
    'Coffee':'Southeast Georgia', 'Pierce':'Southeast Georgia', 'Ware':'Southeast Georgia',
    # Southwest Georgia (5)
    'Baker':'Southwest Georgia', 'Calhoun':'Southwest Georgia', 'Decatur':'Southwest Georgia',
    'Grady':'Southwest Georgia', 'Mitchell':'Southwest Georgia',
    # TLC (15)
    'Bleckley':'TLC', 'Candler':'TLC', 'Dodge':'TLC', 'Emanuel':'TLC', 'Jefferson':'TLC',
    'Johnson':'TLC', 'Laurens':'TLC', 'Montgomery':'TLC', 'Pulaski':'TLC', 'Telfair':'TLC',
    'Toombs':'TLC', 'Treutlen':'TLC', 'Twiggs':'TLC', 'Washington':'TLC', 'Wheeler':'TLC',
    # Towaliga (3)
    'Butts':'Towaliga', 'Lamar':'Towaliga', 'Monroe':'Towaliga',
    # Troup (1)
    'Troup':'Troup',
}

COUNTY_COORDS = {
    'Appling':(31.749,-82.289), 'Atkinson':(31.296,-82.876), 'Bacon':(31.553,-82.453),
    'Baker':(31.326,-84.443), 'Baldwin':(33.072,-83.251), 'Banks':(34.358,-83.5),
    'Barrow':(33.992,-83.714), 'Bartow':(34.239,-84.838), 'Ben Hill':(31.762,-83.218),
    'Berrien':(31.277,-83.227), 'Bibb':(32.803,-83.692), 'Bleckley':(32.437,-83.328),
    'Brantley':(31.2,-81.976), 'Brooks':(30.842,-83.579), 'Bryan':(32.014,-81.444),
    'Bulloch':(32.395,-81.75), 'Burke':(33.06,-81.998), 'Butts':(33.285,-83.955),
    'Calhoun':(31.528,-84.627), 'Camden':(30.929,-81.669), 'Candler':(32.398,-82.077),
    'Carroll':(33.584,-85.084), 'Catoosa':(34.899,-85.138), 'Charlton':(30.785,-82.138),
    'Chatham':(32.003,-81.133), 'Chattahoochee':(32.345,-84.792), 'Chattooga':(34.474,-85.345),
    'Cherokee':(34.242,-84.475), 'Clarke':(33.952,-83.357), 'Clay':(31.626,-84.981),
    'Clayton':(33.547,-84.366), 'Clinch':(30.914,-82.704), 'Cobb':(33.941,-84.576),
    'Coffee':(31.548,-82.853), 'Colquitt':(31.189,-83.767), 'Columbia':(33.544,-82.265),
    'Cook':(31.159,-83.427), 'Coweta':(33.353,-84.767), 'Crawford':(32.717,-83.984),
    'Crisp':(31.922,-83.77), 'Dade':(34.858,-85.504), 'Dawson':(34.44,-84.165),
    'DeKalb':(33.769,-84.224), 'Decatur':(30.878,-84.577), 'Dodge':(32.17,-83.169),
    'Dooly':(32.156,-83.798), 'Dougherty':(31.531,-84.219), 'Douglas':(33.703,-84.769),
    'Early':(31.32,-84.904), 'Echols':(30.712,-82.898), 'Effingham':(32.366,-81.341),
    'Elbert':(34.115,-82.837), 'Emanuel':(32.59,-82.302), 'Evans':(32.157,-81.885),
    'Fannin':(34.866,-84.317), 'Fayette':(33.41,-84.491), 'Floyd':(34.268,-85.211),
    'Forsyth':(34.227,-84.123), 'Franklin':(34.373,-83.236), 'Fulton':(33.788,-84.467),
    'Gilmer':(34.691,-84.453), 'Glascock':(33.239,-82.607), 'Glynn':(31.235,-81.539),
    'Gordon':(34.508,-84.871), 'Grady':(30.875,-84.234), 'Greene':(33.583,-83.169),
    'Gwinnett':(33.962,-84.022), 'Habersham':(34.631,-83.529), 'Hall':(34.318,-83.816),
    'Hancock':(33.274,-83.0), 'Haralson':(33.796,-85.21), 'Harris':(32.735,-84.913),
    'Hart':(34.348,-82.963), 'Heard':(33.297,-85.129), 'Henry':(33.457,-84.163),
    'Houston':(32.457,-83.667), 'Irwin':(31.604,-83.279), 'Jackson':(34.135,-83.568),
    'Jasper':(33.315,-83.688), 'Jeff Davis':(31.805,-82.635), 'Jefferson':(33.057,-82.417),
    'Jenkins':(32.793,-81.962), 'Johnson':(32.709,-82.659), 'Jones':(33.023,-83.56),
    'Lamar':(33.082,-84.144), 'Lanier':(31.038,-83.066), 'Laurens':(32.466,-82.921),
    'Lee':(31.782,-84.145), 'Liberty':(31.824,-81.491), 'Lincoln':(33.792,-82.449),
    'Long':(31.748,-81.746), 'Lowndes':(30.833,-83.267), 'Lumpkin':(34.571,-84.003),
    'Macon':(32.358,-84.044), 'Madison':(34.13,-83.213), 'Marion':(32.354,-84.528),
    'McDuffie':(33.474,-82.48), 'McIntosh':(31.493,-81.408), 'Meriwether':(33.04,-84.686),
    'Miller':(31.165,-84.731), 'Mitchell':(31.224,-84.194), 'Monroe':(33.01,-83.92),
    'Montgomery':(32.173,-82.529), 'Morgan':(33.59,-83.489), 'Murray':(34.79,-84.747),
    'Muscogee':(32.51,-84.876), 'Newton':(33.557,-83.851), 'Oconee':(33.84,-83.436),
    'Oglethorpe':(33.881,-83.076), 'Paulding':(33.92,-84.863), 'Peach':(32.573,-83.825),
    'Pickens':(34.465,-84.468), 'Pierce':(31.36,-82.214), 'Pike':(33.094,-84.386),
    'Polk':(34.004,-85.184), 'Pulaski':(32.226,-83.47), 'Putnam':(33.325,-83.373),
    'Quitman':(31.865,-85.021), 'Rabun':(34.882,-83.407), 'Randolph':(31.761,-84.755),
    'Richmond':(33.359,-82.074), 'Rockdale':(33.652,-84.034), 'Schley':(32.264,-84.317),
    'Screven':(32.75,-81.612), 'Seminole':(30.941,-84.866), 'Spalding':(33.265,-84.287),
    'Stephens':(34.55,-83.29), 'Stewart':(32.077,-84.838), 'Sumter':(32.04,-84.196),
    'Talbot':(32.699,-84.537), 'Taliaferro':(33.568,-82.879), 'Tattnall':(32.044,-82.051),
    'Taylor':(32.557,-84.247), 'Telfair':(31.931,-82.933), 'Terrell':(31.774,-84.444),
    'Thomas':(30.864,-83.919), 'Tift':(31.458,-83.525), 'Toombs':(32.119,-82.325),
    'Towns':(34.915,-83.74), 'Treutlen':(32.403,-82.566), 'Troup':(33.033,-85.03),
    'Turner':(31.714,-83.624), 'Twiggs':(32.666,-83.421), 'Union':(34.829,-83.988),
    'Upson':(32.879,-84.301), 'Walker':(34.734,-85.302), 'Walton':(33.78,-83.733),
    'Ware':(31.059,-82.422), 'Warren':(33.409,-82.678), 'Washington':(32.972,-82.794),
    'Wayne':(31.551,-81.921), 'Webster':(32.045,-84.554), 'Wheeler':(32.123,-82.726),
    'White':(34.643,-83.748), 'Whitfield':(34.813,-84.961), 'Wilcox':(31.969,-83.436),
    'Wilkes':(33.78,-82.74), 'Wilkinson':(32.803,-83.172), 'Worth':(31.549,-83.852),
}

GA_COUNTY_FIPS = {
    'Appling':'13001', 'Atkinson':'13003', 'Bacon':'13005', 'Baker':'13007', 'Baldwin':'13009',
    'Banks':'13011', 'Barrow':'13013', 'Bartow':'13015', 'Ben Hill':'13017', 'Berrien':'13019',
    'Bibb':'13021', 'Bleckley':'13023', 'Brantley':'13025', 'Brooks':'13027', 'Bryan':'13029',
    'Bulloch':'13031', 'Burke':'13033', 'Butts':'13035', 'Calhoun':'13037', 'Camden':'13039',
    'Candler':'13043', 'Carroll':'13045', 'Catoosa':'13047', 'Charlton':'13049',
    'Chatham':'13051', 'Chattahoochee':'13053', 'Chattooga':'13055', 'Cherokee':'13057',
    'Clarke':'13059', 'Clay':'13061', 'Clayton':'13063', 'Clinch':'13065', 'Cobb':'13067',
    'Coffee':'13069', 'Colquitt':'13071', 'Columbia':'13073', 'Cook':'13075', 'Coweta':'13077',
    'Crawford':'13079', 'Crisp':'13081', 'Dade':'13083', 'Dawson':'13085', 'DeKalb':'13089',
    'Decatur':'13087', 'Dodge':'13091', 'Dooly':'13093', 'Dougherty':'13095', 'Douglas':'13097',
    'Early':'13099', 'Echols':'13101', 'Effingham':'13103', 'Elbert':'13105', 'Emanuel':'13107',
    'Evans':'13109', 'Fannin':'13111', 'Fayette':'13113', 'Floyd':'13115', 'Forsyth':'13117',
    'Franklin':'13119', 'Fulton':'13121', 'Gilmer':'13123', 'Glascock':'13125', 'Glynn':'13127',
    'Gordon':'13129', 'Grady':'13131', 'Greene':'13133', 'Gwinnett':'13135',
    'Habersham':'13137', 'Hall':'13139', 'Hancock':'13141', 'Haralson':'13143',
    'Harris':'13145', 'Hart':'13147', 'Heard':'13149', 'Henry':'13151', 'Houston':'13153',
    'Irwin':'13155', 'Jackson':'13157', 'Jasper':'13159', 'Jeff Davis':'13161',
    'Jefferson':'13163', 'Jenkins':'13165', 'Johnson':'13167', 'Jones':'13169', 'Lamar':'13171',
    'Lanier':'13173', 'Laurens':'13175', 'Lee':'13177', 'Liberty':'13179', 'Lincoln':'13181',
    'Long':'13183', 'Lowndes':'13185', 'Lumpkin':'13187', 'Macon':'13193', 'Madison':'13195',
    'Marion':'13197', 'McDuffie':'13189', 'McIntosh':'13191', 'Meriwether':'13199',
    'Miller':'13201', 'Mitchell':'13205', 'Monroe':'13207', 'Montgomery':'13209',
    'Morgan':'13211', 'Murray':'13213', 'Muscogee':'13215', 'Newton':'13217', 'Oconee':'13219',
    'Oglethorpe':'13221', 'Paulding':'13223', 'Peach':'13225', 'Pickens':'13227',
    'Pierce':'13229', 'Pike':'13231', 'Polk':'13233', 'Pulaski':'13235', 'Putnam':'13237',
    'Quitman':'13239', 'Rabun':'13241', 'Randolph':'13243', 'Richmond':'13245',
    'Rockdale':'13247', 'Schley':'13249', 'Screven':'13251', 'Seminole':'13253',
    'Spalding':'13255', 'Stephens':'13257', 'Stewart':'13259', 'Sumter':'13261',
    'Talbot':'13263', 'Taliaferro':'13265', 'Tattnall':'13267', 'Taylor':'13269',
    'Telfair':'13271', 'Terrell':'13273', 'Thomas':'13275', 'Tift':'13277', 'Toombs':'13279',
    'Towns':'13281', 'Treutlen':'13283', 'Troup':'13285', 'Turner':'13287', 'Twiggs':'13289',
    'Union':'13291', 'Upson':'13293', 'Walker':'13295', 'Walton':'13297', 'Ware':'13299',
    'Warren':'13301', 'Washington':'13303', 'Wayne':'13305', 'Webster':'13307',
    'Wheeler':'13309', 'White':'13311', 'Whitfield':'13313', 'Wilcox':'13315', 'Wilkes':'13317',
    'Wilkinson':'13319', 'Worth':'13321',
}

REGIONS = [
    ('Central', [
        'Advo-Kids', 'Ocmulgee', 'Central Georgia', 'Towaliga', 'Houston', 'TLC', 'Troup',
        'Coweta',
    ]),
    ('Metro', [
        'Atlanta', 'Henry', "Children's Voice", 'Clayton', 'DeKalb', 'Gwinnett', 'Cobb',
        'Rockdale', 'Forsyth', 'Alcovy',
    ]),
    ('NE', [
        'Piedmont', 'Athens-Oconee', 'Enotah', 'Hall-Dawson', 'Northeast Georgia',
        'Northern',
    ]),
    ('NW', [
        'Northwest Ga', 'Cherokee CASA', 'Paulding', 'Appalachian', 'Floyd',
        'Polk/Haralson', 'Murray/Whitfield', 'Lookout Mt.', 'Carroll',
    ]),
    ('Coastal', [
        'Atlantic Area', 'Glynn', 'Augusta', 'Ogeechee', 'Savannah-Chatham',
        'Southeast Georgia',
    ]),
    ('South', [
        'Lowndes & Echols', 'Southwest Georgia', 'SOWEGA', 'Chattahoochee', 'CASA Kids',
        'Alapaha', 'Coastal Plain', 'Dougherty',
    ]),
]
