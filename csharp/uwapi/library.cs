using System.IO;
using System;
using System.Runtime.InteropServices;

namespace Unnatural
{
    public static class InteropHelpers
    {
        public static uint[] Ids(Interop.UwIds ids)
        {
            uint[] tmp = new uint[ids.count];
            if (ids.count > 0)
                Marshal.Copy(ids.ids, (int[])(object)tmp, 0, (int)ids.count);
            return tmp;
        }
    }

    public static class LibraryHelpers
    {
        public static string LibraryPath()
        {
            string root = Environment.GetEnvironmentVariable("UNNATURAL_ROOT");
            if (root == null)
            {
                string cwd = Directory.GetCurrentDirectory();
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows) && Directory.GetFiles(cwd, Interop.LibName + ".dll").Length > 0)
                    root = cwd;
                else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux) && Directory.GetFiles(cwd, "lib" + Interop.LibName + ".so").Length > 0)
                    root = cwd;
            }
            if (root == null)
            {
                if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
                    root = "C:/Program Files (x86)/Steam/steamapps/common/Unnatural Worlds/bin";
                else
                    root = Environment.GetEnvironmentVariable("HOME") + "/.steam/steam/steamapps/common/Unnatural Worlds/bin";
            }
            return root;
        }

        public static void SetCurrentDirectory()
        {
            string root = LibraryPath();
            Console.WriteLine("looking for uw library in: " + root);
            Directory.SetCurrentDirectory(root);
        }
    }
}
