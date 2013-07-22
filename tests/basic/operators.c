
void printf(char *,...);

int 
main ()
{
	
	int x,y,z;
	
	y = 0x3424135f;
	z = 0xef543342;
	
	x = y | z;
	printf("%d\n",x);
	x = y & z;
	printf("%d\n",x);
	x = y ^ z;
	printf("%d\n",x);
	x = y + z;
	printf("%d\n",x);
	x = y - z;
	printf("%d\n",x);
	x = y >> z;
	printf("%d\n",x);
	x = y << z;
	printf("%d\n",x);
	x = y * z;
	printf("%d\n",x);
	x = y / z;
	printf("%d\n",x);
	x = y % z;
	printf("%d\n",x);
	x = y > z;
	printf("%d\n",x);
	x = y < z;
	printf("%d\n",x);
	x = y <= z;
	printf("%d\n",x);
	x = y >= z;
	printf("%d\n",x);
	x = y == z;
	printf("%d\n",x);
	x = y != z;
	printf("%d\n",x);
	
	printf("%d\n",~y);
	printf("%d\n",!y);
	printf("%d\n",-y);
	
	
	return 0;
}
