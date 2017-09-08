#!/usr/bin/env python
# Formation of three drones
#
#       *
#      - -
#     * - *
#
# Author: Peng Wei

import rospy
import tf
import math

from sensor_msgs.msg import Joy
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Pose

import math

class Formation():
	def __init__(self):
		self.x_leader 	 = 0.0
		self.y_leader 	 = 0.0
		self.z_leader 	 = 0.5
		self.yaw_leader  = 0.0
		self.x_max = 0.5
		self.y_max = 0.5
		self.z_max = 1.0
		self.yaw_max = 100
		self.r1 = [0.577, 0.0, 0.0]
		self.r2 = [-0.289, 0.5, 0.0]
		self.r3 = [-0.289, -0.5, 0.0]
		self.phi = 0.0
		self.theta = 0.0
		self.psi = 0.0
		
		self.msg = PoseStamped()
		self.msg.header.seq = 0
		self.msg.header.stamp = rospy.Time.now()
		self.msg.header.frame_id = "/leader"
    		self.start_time = self.msg.header.stamp
	    	self.msg.pose.position.x = self.x_leader
	    	self.msg.pose.position.y = self.y_leader
	    	self.msg.pose.position.z = self.z_leader
	    	quaternion = tf.transformations.quaternion_from_euler(0.0, 0.0, 0.0)
	    	self.msg.pose.orientation.x = quaternion[0]
	    	self.msg.pose.orientation.y = quaternion[1]
	    	self.msg.pose.orientation.z = quaternion[2]
	    	self.msg.pose.orientation.w = quaternion[3]

	def rotation(self, source, phi, theta, psi):
		sp    = math.sin(phi);
		cp    = math.cos(phi);
		st    = math.sin(theta);
		ct    = math.cos(theta);
	    	ss    = math.sin(psi);
	    	cs    = math.cos(psi);
		target = [0.0]*3
		target[0] = ct*cs*source[0] + (sp*st*cs-cp*ss)*source[1] +(cp*st*cs+sp*ss)*source[2];
	    	target[1] = ct*ss*source[0] + (sp*st*ss+cp*cs)*source[1] + (cp*st*ss-sp*cs)*source[2];
	    	target[2] = -st*source[0] + sp*ct*source[1] + cp*ct*source[2];
		return target

	def subordinate(self,index):

		if index == 1:
			r = self.r1
		elif index == 2:
			r = self.r2
		elif index ==3:
			r = self.r3
		
		rel = self.rotation(r,self.phi,self.theta,self.psi)
		msg = PoseStamped()
		msg.header.stamp = rospy.Time.now()
		msg.header.frame_id = "/follower"
	    	msg.pose.position.x = self.msg.pose.position.x+rel[0]
	    	msg.pose.position.y = self.msg.pose.position.y+rel[1]
	    	msg.pose.position.z = self.msg.pose.position.z+rel[2]
	    	quaternion = tf.transformations.quaternion_from_euler(0.0,0.0,0.0)
	    	msg.pose.orientation.x = quaternion[0]
	    	msg.pose.orientation.y = quaternion[1]
	    	msg.pose.orientation.z = quaternion[2]
	    	msg.pose.orientation.w = quaternion[3]
		#if index ==1 :
			#rospy.loginfo("goal1, x = %f, y= %f, z= %f", msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
		return msg	 			   				

	
	def linear_map(self, x, r1_min, r1_max, r2_min, r2_max):
		return (x-r1_min)/(r1_max-r1_min)*(r2_max-r2_min)+r2_min

	def update(self, data):
		current_time = rospy.Time.now()
		dt = current_time.to_sec() - self.start_time.to_sec();

		self.msg.pose.position.x = self.linear_map(-data.axes[0],-1, 1, self.x_leader-self.x_max, self.x_leader+self.x_max)
		self.msg.pose.position.y = self.linear_map( data.axes[1],-1, 1, self.y_leader-self.y_max, self.y_leader+self.y_max)
		self.msg.pose.position.z = self.linear_map( data.axes[3],-1, 1, 0, self.z_max)
		
		yaw =  self.linear_map(data.axes[2],-1, 1, -math.radians(self.yaw_max), math.radians(self.yaw_max))
		quaternion = tf.transformations.quaternion_from_euler(0, 0, yaw)
		self.msg.pose.orientation.x = quaternion[0]
		self.msg.pose.orientation.y = quaternion[1]
		self.msg.pose.orientation.z = quaternion[2]
		self.msg.pose.orientation.w = quaternion[3]

		[self.phi,self.theta,self.psi] = tf.transformations.euler_from_quaternion([self.msg.pose.orientation.x,
							 				   self.msg.pose.orientation.y,
							 				   self.msg.pose.orientation.z,
											   self.msg.pose.orientation.w])

		#rospy.loginfo("Time: %f, x = %f, y= %f, z= %f", dt, self.msg.pose.position.x, self.msg.pose.position.y,self.msg.pose.position.z)

		

if __name__ == '__main__':
	rospy.init_node('formation')
	name = rospy.get_param("~name", "/goal")     # publish to
	r = rospy.get_param("~rate", 50.0)	    # frequency 
	rate = rospy.Rate(r)
	
	goal = Formation()
	rospy.Subscriber('/joy', Joy, goal.update)
	pub  = rospy.Publisher("/goal", PoseStamped, queue_size=5)
	pub1 = rospy.Publisher("/goal1", PoseStamped, queue_size=5)
	pub2 = rospy.Publisher("/goal2", PoseStamped, queue_size=5)
	pub3 = rospy.Publisher("/goal3", PoseStamped, queue_size=5)

	while not rospy.is_shutdown():
		goal.msg.header.seq += 1
		goal.msg.header.stamp = rospy.Time.now()
 		pub.publish(goal.msg)
		pub1.publish(goal.subordinate(1))
		pub2.publish(goal.subordinate(2))
		pub3.publish(goal.subordinate(3))
		rate.sleep()
