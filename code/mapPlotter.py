import math
import folium
import matplotlib
import config

R = config.EARTH_RADIUS


def to_radiants(degrees):
    radiants = degrees * math.pi / 180
    return radiants


def to_degrees(radiants):
    degrees = radiants * 180 / math.pi
    return degrees


def waypoint(phi_1, gamma_1, theta, d):
    phi_2 = math.asin(math.sin(phi_1) * math.cos(d/R) + math.cos(phi_1) * math.sin(d/R) * math.cos(theta))
    gamma_2 = gamma_1 + math.atan2(math.sin(theta) * math.sin(d/R) * math.cos(phi_1),
                                   math.cos(d/R) - math.sin(phi_1) * math.sin(phi_2))
    # normalize between [-180°, +180°]
    gamma_2 = (gamma_2 + 3 * math.pi) % (2 * math.pi) - math.pi
    return phi_2, gamma_2


if __name__ == "__main__":
    # Valparaiso
    phi_v = to_radiants(41.47)
    gamma_v = to_radiants(-87)
    # Shangai
    phi_s = to_radiants(31.4)
    gamma_s = to_radiants(121.8)
    # Compute d and theta
    d = R * math.acos(math.sin(phi_v) * math.sin(phi_s) + math.cos(phi_v) * math.cos(phi_s) * math.cos(gamma_s - gamma_v))
    theta = math.atan2(math.sin(gamma_s - gamma_v) * math.cos(phi_s),
                       math.cos(phi_v) * math.sin(phi_s) - math.sin(phi_v) * math.cos(phi_s) * math.cos(gamma_s - gamma_v))

    #a = waypoint(phi_v, phi_s, theta, d)
    markers = []
    waypoints = []
    d_step = 1000
    for i in range(0, math.floor(d), d_step):
        w = waypoint(phi_v, phi_s, theta, i)
        waypoints.append(w)

    for w in waypoints:
        lat = to_degrees(w[0])
        long = to_degrees((w[1]))
        marker = [lat, long]
        markers.append(marker)

    # markers.append([31.4, 121.8])

    fig5 = folium.Figure(height=550, width=750)
    m5 = folium.Map(location=markers[0], tiles='cartodbpositron', zoom_start=5)
    fig5.add_child(m5)

    line_1 = folium.vector_layers.PolyLine(markers, popup='<b>Path</b>', tooltip='Vehicle', color='blue', weight=5).add_to(m5)
    folium.LayerControl().add_to(m5)

    m5.save('test.html')

    print("Done")
