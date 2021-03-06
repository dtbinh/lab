#!/usr/bin/env python
# Formation of three drones
#
#     * - *
#     - - -
#     * - *
#
# Author: Peng Wei

import rospy
import tf
import math

from std_srvs.srv import Empty, EmptyResponse
from sensor_msgs.msg import Joy
from geometry_msgs.msg import PoseStamped
import math

class Heading():
	def __init__(self, x, y, z, yaw, cmd, delay, bias):
		self.yaw_max 	= 100
		self.initial_yaw = yaw*3.1416/180.0
		self.msg = PoseStamped()
		self.msg.pose.position.x = x
		self.msg.pose.position.y = y
		self.msg.pose.position.z = z
		self.cmd = cmd
		self.delay = delay
		self.bias = bias

		self.listener_yaw = self.initial_yaw
		self.talker1_yaw = self.initial_yaw
		self.listener_previous = PoseStamped()
		self.state = 'stand-by'
		rospy.Service('/consensus', Empty, self.switch2consensus)
		rospy.Service('/standby', Empty, self.switch2standby)
		
	def switch2consensus(self, req):
		self.state = 'consensus'
		self.previous_time = rospy.Time.now()
		#self.previous_value = self.initial_yaw
		rospy.loginfo("Start!")
		bag.close()
		return EmptyResponse()

	def switch2standby(self, req):
		self.state = 'stand-by'
		self.previous_time = rospy.Time.now()
		#self.previous_value = self.initial_yaw
		rospy.loginfo("Stop!")
		return EmptyResponse()

	#def update_joy(self, data):
		#self.data = data

	def update_listener(self, data):
		(roll,pitch,yaw) = tf.transformations.euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,\
							data.pose.orientation.z,data.pose.orientation.w])
		self.listener_yaw = yaw

	def update_talker1(self, data):
		(roll,pitch,yaw) = tf.transformations.euler_from_quaternion([data.pose.orientation.x,data.pose.orientation.y,\
							data.pose.orientation.z,data.pose.orientation.w])
		self.talker1_yaw = yaw + self.bias

	def update(self):
		if self.state == 'stand-by': 
			self.msg.header.stamp = rospy.Time.now()
			quaternion = tf.transformations.quaternion_from_euler(0.0, 0.0, self.initial_yaw)
			self.msg.pose.orientation.x = quaternion[0]
			self.msg.pose.orientation.y = quaternion[1]
			self.msg.pose.orientation.z = quaternion[2]
			self.msg.pose.orientation.w = quaternion[3]
		elif self.state == 'consensus':
			self.msg.header.stamp = rospy.Time.now()
			current_time = rospy.Time.now()
			dt = current_time.to_sec() - self.previous_time.to_sec();
			x_dot = 0.1*(self.talker1_yaw-self.listener_yaw) - 1.0*(self.listener_yaw-self.cmd)
			yaw = self.listener_yaw + x_dot*dt
			quaternion = tf.transformations.quaternion_from_euler(0.0, 0.0, yaw)
			self.msg.pose.orientation.x = quaternion[0]
			self.msg.pose.orientation.y = quaternion[1]
			self.msg.pose.orientation.z = quaternion[2]
			self.msg.pose.orientation.w = quaternion[3]
			self.previous_time = current_time


if __name__ == '__main__':
	rospy.init_node('heading')
	listener = rospy.get_param("~listener")
	talker1 = rospy.get_param("~talker1")
	#talker2 = rospy.get_param("talker2")
	x = rospy.get_param("~x")
	y = rospy.get_param("~y")
	z = rospy.get_param("~z")
	yaw = rospy.get_param("~yaw")
	cmd = rospy.get_param("~cmd")
	delay = rospy.get_param("~delay", 0.0)
	bias = rospy.get_param("~bias", 0.0)

	r    = rospy.get_param("~rate", 50.0)	    # frequency 
	rate = rospy.Rate(r)
	goal = Heading(x,y,z,yaw,cmd,delay,bias)
	
	#rospy.Subscriber('/joy', Joy, goal.update_joy)
	rospy.Subscriber(listener, PoseStamped, goal.update_listener)
	rospy.Subscriber(talker1, PoseStamped, goal.update_talker1)
	pub = rospy.Publisher("goal", PoseStamped, queue_size=1)

	while not rospy.is_shutdown():
		goal.update()
		pub.publish(goal.msg)
		rate.sleep()
